from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import authentication, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .middlewares import professors_only, students_only
from . import models, serializers


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
    profile = models.Profile.objects.get(user=request.user)
    return Response(serializers.ProfileSerializer(profile).data)


@api_view(['POST'])
def create_profile_view(request):
    serializer = serializers.SignUpSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors)

    data = serializer.validated_data
    email = data['email']
    if User.objects.filter(username=email).exists():
        return Response({
            'error': f"User with email {email} already exists"
        })

    user = User.objects.create_user(username=email, password=data["password"])
    profile = models.Profile.objects.create(
        name=data['name'],
        user=user,
        user_type=data['user_type'],
        program=data['program'] if 'program' in data.keys() else ""
    )

    return Response(serializers.ProfileSerializer(profile).data)


#
# @api_view(['GET'])
# @authentication_classes([authentication.TokenAuthentication])
# @permission_classes([permissions.IsAuthenticated])
# @group_required('Students')
# def get_student_deliverables(request):
#     profile = models.Profile.objects.get(user=request.user)
#     deliverables = models.Deliverable.objects.filter(course__students__user=request.user)
#     return Response(serializers.DeliverableSerializer(deliverables, many=True).data)


@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@students_only
def get_student_deliverable_submissions(request):
    profile = models.Profile.objects.get(user=request.user)
    deliverable_submissions = models.DeliverableSubmission.objects.filter(submitter=profile)
    return Response(serializers.DeliverableSubmissionSerializer(deliverable_submissions, many=True).data)


@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@professors_only
def create_deliverable(request):
    serializer = serializers.DeliverableSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors)

    data = serializer.validated_data
    deliverable = models.Deliverable.objects.create(
        name=data["name"],
        course=data["course"],
        is_group_work=data["is_group_work"],
        description=data["description"],
        deadline=data["deadline"],
        total_score=data["total_score"]
    )

    return Response(serializers.DeliverableSerializer(data=deliverable).data)