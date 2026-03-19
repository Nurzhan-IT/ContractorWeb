from django.middleware.csrf import get_token


class EnsureCsrfCookieMiddleware:
    """Force the CSRF cookie to be set on every response.

    Jinja2 templates don't render {% csrf_token %} automatically, so Django's
    CsrfViewMiddleware never gets the signal to set the cookie. This middleware
    calls get_token() on every request, which marks the cookie for inclusion in
    the response — making it available to JS fetch() POST calls via getCookie().
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        get_token(request)  # marks CSRF_COOKIE_NEEDS_UPDATE on the request
        return self.get_response(request)
