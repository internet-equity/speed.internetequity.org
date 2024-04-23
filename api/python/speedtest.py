"""API speedtest endpoint"""
import boto3
import json
import os
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

from lib import cors, http_context, response


ALLOWED_METHODS = {'POST'}

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').lower().split()

ALLOWED_ORIGIN = os.getenv('ALLOWED_ORIGIN', '').strip() or None

ALLOWED_PATHS = os.getenv('ALLOWED_PATHS', '').split() or {'/speedtest'}

STORE_PATH = os.getenv('STORE_PATH', '').strip()  # either s3://... or file://...


@http_context
@cors(ALLOWED_ORIGIN)
def main(request, context):
    """Persist a speedtest results record"""
    if request.headers.get('host').lower() not in ALLOWED_HOSTS:
        return response.response_400()

    if request.path not in ALLOWED_PATHS:
        return response.response_404()

    if request.method not in ALLOWED_METHODS:
        return response.response_405()

    origin = request.headers.get('origin')

    try:
        # we don't expect multivalue items so won't use parse_qs
        measurement = dict(urllib.parse.parse_qsl(request.body))
    except ValueError:
        print(f"ERROR: could not parse body from {request.sourceIp} at {origin}: {request.body}")
        return response.response_400("bad encoding")

    try:
        request_datetime = datetime.strptime(context.time, '%d/%b/%Y:%H:%M:%S %z')
    except (TypeError, ValueError):
        request_datetime = None

    operation_datetime = datetime.now(timezone.utc)

    try:
        data = {
            'origin': origin,
            'ip_address': request.sourceIp,
            'user_agent': request.userAgent,
            'data': {
                'download': float(measurement['d']),
                'upload': float(measurement['u']),
                'latency': float(measurement['p']),
                'jitter': float(measurement['j']),
                'download_size': float(measurement['dd']),
                'upload_size': float(measurement['ud']),
                'user_agent': measurement['ua'],
            },
            'datetime': request_datetime and request_datetime.strftime('%Y-%m-%dT%H:%M:%S%z'),
        }
    except KeyError:
        return response.response_400("missing parameters")
    except ValueError:
        return response.response_400("unexpected values")

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
            return response.response_503()
    else:
        print(f"ERROR: bad configuration value for STORE_PATH: {STORE_PATH!r}")
        return response.response_500()

    return response.response_201()
