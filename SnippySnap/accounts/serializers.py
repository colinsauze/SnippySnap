from rest_framework import serializers
from api import serializers as api_serializers
from django.contrib.auth.models import User
from . import models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

class ProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=True)

    class Meta:
        fields = ['user', 'display_name']
        model = models.Profile
