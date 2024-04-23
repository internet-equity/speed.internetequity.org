import base64
import functools
import types


CORE_REQUEST_KEYS = ('method', 'path', 'protocol', 'sourceIP', 'userAgent')

CORE_CONTEXT_KEYS = ('accountId', 'apiId', 'domainName', 'domainPrefix', 'requestId',
                     'routeKey', 'stage', 'time', 'timeEpoch')


def make_request(event, meta: bool):
    """Map platform event to convenient request and optional request
    context object(s).

    """
    body = event.get("body", '')
    cookies = event.get('cookies', [])
    headers = event.get('headers', {})
    isBase64Encoded = event.get("isBase64Encoded")

    platform_request_context = event.get('requestContext', {})
    platform_request = platform_request_context.get('http', {})

    core_request = dict.fromkeys(CORE_REQUEST_KEYS)
    core_request.update(platform_request)

    request = types.SimpleNamespace(
        body=base64.b64decode(body).decode() if isBase64Encoded else body,
        body_raw=body,
        cookies=cookies,
        headers={key.lower(): value for (key, value) in headers.items()},
        **core_request,
    )

    if meta:
        core_request_context = dict.fromkeys(CORE_CONTEXT_KEYS)
        core_request_context.update(platform_request_context)

        request_context = types.SimpleNamespace(
            isBase64Encoded=isBase64Encoded,
            **core_request_context,
        )

        return (request, request_context)

    return request


def http_decorate(func, meta: bool):
    """Decorator to map platform event to convenient request and
    optional request context object(s).

    """
    @functools.wraps(func)
    def wrapped(event, _context):
        return func(*make_request(event, meta))

    return wrapped


http = functools.partial(http_decorate, meta=False)

http_context = functools.partial(http_decorate, meta=True)
