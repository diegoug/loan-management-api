from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import UserAPIKey

import logging

logger = logging.getLogger(__name__)


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('Authorization')

        if not api_key:
            logger.debug('No API key provided')
            return None  # No se proporciona API key

        # Remover el prefijo 'Api-Key' si se está usando
        if api_key.startswith('Api-Key '):
            api_key = api_key.split(' ')[1]

        try:
            api_key_obj = UserAPIKey.objects.get_from_key(api_key)
        except UserAPIKey.DoesNotExist:
            logger.debug('Invalid API key provided')
            raise AuthenticationFailed('Invalid API key')

        # Obtener el usuario asociado a la clave API.
        user = api_key_obj.user
        if user is None:
            logger.debug('No user associated with this API key')
            raise AuthenticationFailed('No user associated with this API key')

        logger.debug('User authenticated successfully')
        return (user, api_key_obj)
