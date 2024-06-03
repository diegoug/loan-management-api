from django.db import models
from django.contrib.auth.models import User
from rest_framework_api_key.models import AbstractAPIKey


class UserAPIKey(AbstractAPIKey):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
