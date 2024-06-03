from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings

from rest_framework_api_key.models import APIKey
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from .authentication import APIKeyAuthentication
from .permissions import HasCustomAPIKey
from .models import UserAPIKey


class RegisterAdminView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        secret_key = request.data.get('secret_key')
        username = request.data.get('username')
        password = request.data.get('password')

        if not secret_key:
            return JsonResponse({'error': 'Missing required parameter: secret_key'}, status=400)
        if not username:
            return JsonResponse({'error': 'Missing required parameter: username'}, status=400)
        if not password:
            return JsonResponse({'error': 'Missing required parameter: password'}, status=400)

        if secret_key != settings.SINGLE_USE_CREATE_CUSTOMER_SECRET_KEY:
            return JsonResponse({'error': 'Invalid secret key', 'detail': 'The provided secret key is incorrect. Please use the correct key to create an admin user.'}, status=403)

        if User.objects.filter(is_superuser=True).exists():
            return JsonResponse({'error': 'Admin user already exists', 'detail': 'There is already an admin user in the system. This is a single use endpoint.'}, status=400)

        user = User.objects.create_superuser(username=username, password=password)
        api_key, key = UserAPIKey.objects.create_key(name=user.username, user=user)
        
        return JsonResponse({'message': 'Admin user created successfully', 'api_key': key}, status=201)


class RegisterUserView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [HasCustomAPIKey]

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Permission denied. Only admins can create users.'}, status=403)

        username = request.data.get('username')
        password = request.data.get('password')
        is_admin = request.data.get('is_admin', False)

        if not username:
            return JsonResponse({'error': 'Missing required parameter: username'}, status=400)
        if not password:
            return JsonResponse({'error': 'Missing required parameter: password'}, status=400)

        if is_admin:
            user = User.objects.create_superuser(username=username, password=password)
        else:
            user = User.objects.create_user(username=username, password=password)

        api_key, key = APIKey.objects.create_key(name=username)
        
        return JsonResponse({'message': 'User created successfully', 'api_key': key}, status=201)

