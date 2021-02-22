from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['name', 'user_type', 'program']


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    name = serializers.CharField(required=True, max_length=128)
    user_type = serializers.CharField(required=True, max_length=2)
    program = serializers.CharField(required=True, max_length=128)
