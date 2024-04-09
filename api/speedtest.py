import base64
import boto3
import json
import os
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_METHODS = {'POST'}

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split()

ALLOWED_PATHS = os.getenv('ALLOWED_PATHS', '').split() or {'/speedtest/'}

STORE_PATH = os.getenv('STORE_PATH', '').strip()  # either s3://... or file://...


def main(event, _context):
    headers = event.get('headers', {})

    requestContext = event.get('requestContext', {})
    request = requestContext.get('http', {})

    if headers.get('Host') not in ALLOWED_HOSTS:
        return response_400()

    if request.get("path") not in ALLOWED_PATHS:
        return response_404()

    if request.get('method') not in ALLOWED_METHODS:
        return response_405()

    origin = headers.get('Origin')
    ip_address = request.get('sourceIp')
    user_agent = request.get('userAgent')

    raw = event.get("body", '')
    form = base64.b64decode(raw) if event.get("isBase64Encoded") else raw

    try:
        # we don't expect multivalue items so won't use parse_qs
        body = dict(urllib.parse.parse_qsl(form))
    except ValueError:
        print(f"ERROR: could not parse body from {ip_address} to {origin}: {form}")
        return response_400("bad encoding")

    request_time = requestContext.get('time', '')

    try:
        request_datetime = datetime.strptime(request_time, '%d/%b/%Y:%H:%M:%S %z')
    except ValueError:
        request_datetime = None

    operation_datetime = datetime.now(timezone.utc)

    try:
        data = {
            'origin': origin,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'data': {
                'download': float(body['d']),
                'upload': float(body['u']),
                'latency': float(body['p']),
                'jitter': float(body['j']),
                'download_size': float(body['dd']),
                'upload_size': float(body['ud']),
                'user_agent': body['ua'],
            },
            'datetime': request_datetime.strftime('%Y-%m-%dT%H:%M:%S%z'),
        }
    except KeyError:
        return response_400("missing parameters")
    except ValueError:
        return response_400("unexpected values")

    result_name = f'result-{operation_datetime:%Y%m%dT%H%M%S}-speedtest.json'

    if STORE_PATH.startswith('file://'):
        store_path = Path(STORE_PATH[7:])
        store_path.mkdir(exist_ok=True)

        with store_path.joinpath(result_name).open('w') as fd:
            json.dump(data, fd)
    elif STORE_PATH.startswith('s3://'):
        (bucket, *prefix_part) = STORE_PATH[5:].split('/', 1)

        try:
            s3 = boto3.client('s3')
            s3.put_object(
                Bucket=bucket,
                Key=Path(*prefix_part, result_name).as_posix(),
                Body=json.dumps(data),
                ContentType='application/json',
            )
        except Exception as exc:
            print(f"ERROR: {exc}")
            return response_503()
    else:
        print(f"ERROR: bad configuration value for STORE_PATH: {STORE_PATH!r}")
        return response_500()

    return response_201()


def response_200(message=None):
    return {
        "statusCode": 200,
        "body": json.dumps({
            'error': False,
            'status': 'OK',
            'message': message,
        }),
    }


def response_201(message=None):
    return {
        "statusCode": 201,
        "body": json.dumps({
            'error': False,
            'status': 'Created',
            'message': message,
        }),
    }


def response_400(message=None):
    return {
        "statusCode": 400,
        "body": json.dumps({
            'error': True,
            'status': 'Bad Request',
            'message': message,
        }),
    }


def response_404(message=None):
    return {
        "statusCode": 404,
        "body": json.dumps({
            'error': True,
            'status': 'Not Found',
            'message': message,
        }),
    }


def response_405(message=None):
    return {
        "statusCode": 405,
        "body": json.dumps({
            'error': True,
            'status': 'Method Not Allowed',
            'message': message,
        }),
    }


def response_500(message=None):
    return {
        "statusCode": 500,
        "body": json.dumps({
            'error': True,
            'status': 'Internal Server Error',
            'message': message,
        }),
    }


def response_503(message=None):
    return {
        "statusCode": 503,
        "body": json.dumps({
            'error': True,
            'status': 'Service Unavailable',
            'message': message,
        }),
    }
