import functools
import re
import urllib.parse

from .. import response as responses


class cors:
    """Request-handler decorator to enforce CORS restrictions.

    Wraps the decorated request-handling callable to refuse unauthorized
    cross-origin requests and to set the configured
    `Access-Control-Allow-Origin` header.

    """
    @staticmethod
    def _parse_origin_(origin: str | None) -> urllib.parse.ParseResult | None:
        """Construct an origin URL `ParseResult` from the configured
        origin `str`.

        """
        if origin is None or origin == '*':
            return None

        if re.match(r'(?:[a-z]+:)?//', origin, re.I):
            return urllib.parse.urlparse(origin)

        return urllib.parse.urlparse(f'//{origin}')

    def __init__(self, origin: str | None):
        """Configure CORS.

        To enable request- and response-handling, `origin` is set to a `str`, one of either:

        * `*`: requests from any origin are permitted
        * `<my.host>`: requests from the specified origin are permitted

        In either case, the value of `origin` is additionally set in any
        response returned, under the `Access-Control-Allow-Origin` header.

        To disable the function of this decorator, `origin` may be set to `None`.

        """
        self.origin = origin

        self._origin_parsed_ = self._parse_origin_(origin)

    def __call__(self, func):
        """Wrap the decorated request-handling callable to enforce any
        configured CORS restrictions.

        """
        @functools.wraps(func)
        def wrapped(request, *args, **kwargs):
            response = self._process_request_(request)

            if response is None:
                response = func(request, *args, **kwargs)

            return self._process_response_(response)

        return wrapped

    def _match_origin_(self, other: str | None) -> bool | None:
        """Compare the specified origin `other` to the configured origin."""
        if self._origin_parsed_ is None:
            return None

        parsed = urllib.parse.urlparse(other)

        if self._origin_parsed_.scheme and self._origin_parsed_.scheme != parsed.scheme:
            return False

        if self._origin_parsed_.hostname and self._origin_parsed_.hostname != parsed.hostname:
            return False

        if self._origin_parsed_.port is not None and self._origin_parsed_.port != parsed.port:
            return False

        return True

    def _process_request_(self, request):
        """Enforce any configured CORS restrictions on the request.

        Unauthorized cross-origin requests are refused with a returned
        HTTP 400 response.

        """
        if self.origin is None:
            return None

        if self.origin == '*':
            return None

        if self._match_origin_(request.headers.get('origin')):
            return None

        return responses.response_400()

    def _process_response_(self, response):
        """Set any configured CORS restriction with the
        `Access-Control-Allow-Origin` header in the response.

        """
        if self.origin is not None:
            headers = response.setdefault('headers', {})
            headers['access-control-allow-origin'] = self.origin

        return response
