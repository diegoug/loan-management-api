from rest_framework.permissions import BasePermission
from .models import UserAPIKey


class HasCustomAPIKey(BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get('Authorization')

        if not api_key:
            return False

        if api_key.startswith('Api-Key '):
            api_key = api_key.split(' ')[1]

        try:
            api_key_obj = UserAPIKey.objects.get_from_key(api_key)
        except UserAPIKey.DoesNotExist:
            return False

        return not api_key_obj.revoked
