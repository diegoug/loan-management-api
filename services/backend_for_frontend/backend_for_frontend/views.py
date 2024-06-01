# loans/views.py
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@method_decorator(csrf_exempt, name='dispatch')
class RegisterAdminView(View):
    def post(self, request, *args, **kwargs):
        secret_key = request.POST.get('secret_key')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not secret_key:
            return JsonResponse({'error': 'Missing required parameter: secret_key'}, status=400)
        if not username:
            return JsonResponse({'error': 'Missing required parameter: username'}, status=400)
        if not password:
            return JsonResponse({'error': 'Missing required parameter: password'}, status=400)

        if secret_key != settings.SINGLE_USE_ADMIN_SECRET_KEY:
            return JsonResponse({'error': 'Invalid secret key', 'detail': 'The provided secret key is incorrect. Please use the correct key to create an admin user.'}, status=403)

        if User.objects.filter(is_superuser=True).exists():
            return JsonResponse({'error': 'Admin user already exists', 'detail': 'There is already an admin user in the system. This is a single use endpoint.'}, status=400)

        User.objects.create_superuser(username=username, password=password)
        return JsonResponse({'message': 'Admin user created successfully'}, status=201)
