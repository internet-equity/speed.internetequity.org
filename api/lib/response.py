import json


def response_200(message=None):
    return {
        "statusCode": 200,
        'headers': {'content-type': 'application/json'},
        "body": json.dumps({
            'error': False,
            'status': 'OK',
            'message': message,
        }),
    }


def response_201(message=None):
    return {
        "statusCode": 201,
        'headers': {'content-type': 'application/json'},
        "body": json.dumps({
            'error': False,
            'status': 'Created',
            'message': message,
        }),
    }


def response_400(message=None):
    return {
        "statusCode": 400,
        'headers': {'content-type': 'application/json'},
        "body": json.dumps({
            'error': True,
            'status': 'Bad Request',
            'message': message,
        }),
    }


def response_404(message=None):
    return {
        "statusCode": 404,
        'headers': {'content-type': 'application/json'},
        "body": json.dumps({
            'error': True,
            'status': 'Not Found',
            'message': message,
        }),
    }


def response_405(message=None):
    return {
        "statusCode": 405,
        'headers': {'content-type': 'application/json'},
        "body": json.dumps({
            'error': True,
            'status': 'Method Not Allowed',
            'message': message,
        }),
    }


def response_500(message=None):
    return {
        "statusCode": 500,
        'headers': {'content-type': 'application/json'},
        "body": json.dumps({
            'error': True,
            'status': 'Internal Server Error',
            'message': message,
        }),
    }


def response_503(message=None):
    return {
        "statusCode": 503,
        'headers': {'content-type': 'application/json'},
        "body": json.dumps({
            'error': True,
            'status': 'Service Unavailable',
            'message': message,
        }),
    }
