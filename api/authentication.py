from rest_framework.authentication import BaseAuthentication
from .models import MyOwnToken
from django.utils.translation import gettext_lazy as _

from rest_framework import HTTP_HEADER_ENCODING, exceptions


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth

class MyOwnTokenAuthentication(BaseAuthentication):
    keyword = 'Token'
    status = False
    def authenticate_credentials(self, key):
        model = MyOwnToken
        try:
            token = model.objects.select_related('user').get(key=key)
            client = token.user
            client.is_authenticated = True
            client.save()
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)
        return self.authenticate_credentials(token)