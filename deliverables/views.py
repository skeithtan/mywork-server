from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Profile
from .serializers import ProfileSerializer, SignUpSerializer


@api_view(['POST'])
def sign_in_view(request):
    user = authenticate(username=request.data["email"], password=request.data["password"])
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key
        })
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    return Response(ProfileSerializer(profile).data)


@api_view(['POST'])
def create_profile_view(request):
    serializer = SignUpSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors)

    email = serializer.validated_data['email']
    if User.objects.filter(username=email).exists():
        return Response({
            'error': f"User with email {email} already exists"
        })

    user = User.objects.create_user(username=email, password=serializer.validated_data["password"])
    profile = Profile.objects.create(
        name=serializer.validated_data['name'],
        user=user,
        user_type=serializer.validated_data['user_type'],
        program=serializer.validated_data['program']
    )

    return Response(ProfileSerializer(profile).data)
