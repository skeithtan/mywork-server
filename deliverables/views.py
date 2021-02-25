from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import authentication, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import transaction
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
        }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=email, password=data["password"])
    profile = models.Profile.objects.create(
        name=data['name'],
        user=user,
        user_type=data['user_type'],
        program=data['program'] if 'program' in data.keys() else ""
    )

    return Response(serializers.ProfileSerializer(profile).data)


@api_view(['POST', 'DELETE'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@students_only
def members_view(request, id):
    if request.method == 'POST':
        return add_members_view(request, id)
    else:
        return delete_members_view(request, id)


def add_members_view(request, id):
    profile = models.Profile.objects.get(user=request.user)
    deliverable_submission_to_edit = models.DeliverableSubmission.objects.filter(id=id)

    # Check if deliverable submission id exists in db
    if not deliverable_submission_to_edit.exists():
        return Response({
            'error': f"Deliverable submission n°{id} does not exist."
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if deliverable submission is a group work
    if not deliverable_submission_to_edit.get().deliverable.is_group_work:
        return Response({
            'error': f"Deliverable submission n°{id} is NOT a group assignement."
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Check if student email exists
    email = request.data["email"]
    if not models.User.objects.filter(username=email).exists():
        return Response({
            'error': f"Student with email: {email} does not exist."
        }, status=status.HTTP_404_NOT_FOUND)

    # Get profile from email address
    member_to_add = models.User.objects.filter(username=request.data["email"]).get()
    member_profile_to_add = models.Profile.objects.get(user=member_to_add)

    # Check that profile is of student type
    if member_profile_to_add.user_type != models.Profile.UserType.STUDENT:
        return Response({
            'error': f"Profile with email: {email} is not of student type."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if student already exists in course's students list
    group_members = deliverable_submission_to_edit.get().group_members

    if member_profile_to_add in group_members.all():
        return Response({
            "error": "User is already a group member in this deliverable submission !"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Add profile to group_members
    group_members.add(member_profile_to_add)

    return Response(serializers.ProfileSerializer(member_profile_to_add.__dict__).data)


def delete_members_view(request, id):
    profile = models.Profile.objects.get(user=request.user)
    deliverable_submission_to_edit = models.DeliverableSubmission.objects.filter(id=id)

    # Check if deliverable submission id exists in db
    if not deliverable_submission_to_edit.exists():
        return Response({
            'error': f"Deliverable submission n°{id} does not exist."
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if deliverable submission is a group work
    if not deliverable_submission_to_edit.get().deliverable.is_group_work:
        return Response({
            'error': f"Deliverable submission n°{id} is NOT a group assignement."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if student email exists
    email = request.data["email"]
    if not models.User.objects.filter(username=email).exists():
        return Response({
            'error': f"Student with email: {email} does not exist."
        }, status=status.HTTP_404_NOT_FOUND)

    # Get student from email address
    member_to_delete = models.User.objects.filter(username=request.data["email"]).get()
    member_profile_to_delete = models.Profile.objects.get(user=member_to_delete)

    # Check if student already exists in group_members list
    group_members = deliverable_submission_to_edit.get().group_members

    if not member_profile_to_delete in group_members.all():
        return Response({
            "error": "User is NOT a group member in this deliverable submission !"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Delete profile to group_members
    group_members.remove(member_profile_to_delete)

    return Response(serializers.ProfileSerializer(member_profile_to_delete.__dict__).data)


@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@professors_only
def create_deliverable_view(request):
    serializer = serializers.DeliverableSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors)

    data = serializer.validated_data
    print(data)
    course = data["course"]

    with transaction.atomic():
        deliverable = models.Deliverable.objects.create(
            name=data["name"],
            course=course,
            is_group_work=data["is_group_work"],
            description=data["description"],
            deadline=data["deadline"],
            total_score=data["total_score"]
        )

        for student in course.students.all():
            models.DeliverableSubmission.objects.create(
                deliverable=deliverable,
                submitter=student,
            )

    return Response(serializers.DeliverableSerializer(deliverable).data)


@api_view(['GET', 'POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def courses_view(request):
    if request.method == 'GET':
        return get_courses(request)
    else:
        return create_course(request)


def get_courses(request):
    profile = models.Profile.objects.get(user=request.user)
    search = request.query_params['search'] if 'search' in request.query_params else None

    if search:
        # When searching, search from ALL available courses
        courses = models.Course.objects.filter(name__icontains=search)
    else:
        # When not searching, only give courses relevant to the user
        if profile.user_type == models.Profile.UserType.PROFESSOR:
            courses = models.Course.objects.filter(professor=profile)
        else:
            courses = models.Course.objects.filter(students=profile)

    return Response(serializers.CourseSerializer(courses, many=True).data)


@professors_only
def create_course(request):
    profile = models.LinkAttachment.objects.get(user=request.user)
    serializer = serializers.CourseSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors)

    data = serializer.validated_data
    course = models.Course.objects.create(
        name=data["name"],
        semester_name=data["semester_name"],
        professor=profile
    )

    return Response(serializers.CourseSerializer(course).data)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def courses_details_view(request, id):
    if request.method == 'GET':
        return get_courses_details(request, id)
    elif request.method == 'PUT':
        return edit_course(request, id)
    else:
        return drop_course(request, id)


def get_courses_details(request, id):
    profile = models.Profile.objects.get(user=request.user)
    if profile.user_type == models.Profile.UserType.PROFESSOR:
        # Check if professor has access to requested course
        if not models.Course.objects.filter(professor=profile).filter(id=id).exists():
            return Response({
                'error': f"Professors only have access to the courses they created."
            }, status=status.HTTP_401_UNAUTHORIZED)
        course = models.Course.objects.filter(professor=profile).get(id=id)
    else:
        # Check if student has access to requested course
        if not models.Course.objects.filter(students=profile).filter(id=id).exists():
            return Response({
                'error': f"Students only have access to the classes they are a part of."
            }, status=status.HTTP_401_UNAUTHORIZED)
        course = models.Course.objects.filter(students=profile).get(id=id)

    # Return found course if access is allowed
    return Response(serializers.CourseSerializer(course).data)


def edit_course(request, id):
    profile = models.Profile.objects.get(user=request.user)
    if profile.user_type == models.Profile.UserType.PROFESSOR:
        return edit_course_details(request, id)
    else:
        return join_course(request, id)


@professors_only
def edit_course_details(request, id):
    profile = models.Profile.objects.get(user=request.user)
    course_to_edit = models.Course.objects.filter(professor=profile).filter(id=id)
    # Check if professor has access to requested course
    if not course_to_edit.exists():
        return Response({
            'error': f"Professors only have access to the courses they created."
        }, status=status.HTTP_401_UNAUTHORIZED)
    else:

        serializer = serializers.CourseSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors)

        data = serializer.validated_data

        course_to_edit.update(name=data['name'], semester_name=data['semester_name'])

        course_edited = models.Course.objects.filter(professor=profile).get(id=id)

        return Response(serializers.CourseSerializer(course_edited).data)


@students_only
def join_course(request, id):
    profile = models.Profile.objects.get(user=request.user)
    course_to_edit = models.Course.objects.filter(id=id)
    # Check if course exists in db
    if not course_to_edit.exists():
        return Response({
            'error': f"Course n°{id} does not exist. Please choose a valid id."
        }, status=status.HTTP_404_NOT_FOUND)
    else:
        # Check if student already exists in course's students list
        if profile in course_to_edit.get().students.all():
            return Response({
                "error": "You are already enrolled in this course !"
            }, status=status.HTTP_400_BAD_REQUEST)

        course_to_edit.get().students.add(profile)

        course_edited = models.Course.objects.get(id=id)

        return Response(serializers.CourseSerializer(course_edited).data)


@students_only
def drop_course(request, id):
    profile = models.Profile.objects.get(user=request.user)
    course_to_edit = models.Course.objects.filter(id=id)
    # Check if course exists in db
    if not course_to_edit.exists():
        return Response({
            'error': f"Course n°{id} does not exist. Please choose a valid id."
        }, status=status.HTTP_404_NOT_FOUND)
    else:
        # Check if student is currently enrolled in this course
        if profile not in course_to_edit.get().students.all():
            return Response({
                "error": "You are NOT enrolled in this course !"
            }, status=status.HTTP_400_BAD_REQUEST)

        course_to_edit.get().students.remove(profile)

        course_edited = models.Course.objects.get(id=id)

        return Response(serializers.CourseSerializer(course_edited).data)
    
    
@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@students_only
def link_attachment_view(request, id):
    # Check submission id
    deliverable_submission = models.DeliverableSubmission.objects.filter(id=id)
    if not deliverable_submission.exists():
        return Response({
            'error': f"Deliverable Submission n°{id} does not exist. Please choose a valid id."
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = serializers.LinkAttachmentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors)

    data = serializer.validated_data
    link_attachment = models.LinkAttachment.objects.create(
        url=data["url"],
        label=data["label"],
    )

    # Add link to link attachments list
    deliverable_submission.get().link_attachments.add(link_attachment)

    return Response(serializers.StudentDeliverableSubmissionSerializer(deliverable_submission.get()).data)

@api_view(['DELETE'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@students_only
def link_delete_view(request, id, link_id):
    # Check submission id
    deliverable_submission = models.DeliverableSubmission.objects.filter(id=id)
    if not deliverable_submission.exists():
        return Response({
            'error': f"Deliverable Submission n°{id} does not exist. Please choose a valid id."
        }, status=status.HTTP_404_NOT_FOUND)
    link_attachment_to_delete = models.LinkAttachment.objects.filter(id=link_id)

    if not link_attachment_to_delete.exists():
        return Response({
            'error': f"Link n°{link_id} does not exist. Please choose a valid id."
        }, status=status.HTTP_404_NOT_FOUND)

    # Add link to link attachments list
    deliverable_submission.get().link_attachments.remove(link_attachment_to_delete.get())
    
    return Response(serializers.StudentDeliverableSubmissionSerializer(deliverable_submission.get()).data)
    


@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@professors_only
def course_deliverables_view(request, id):
    course = models.Course.objects.get(pk=id)
    deliverables = models.Deliverable.objects.filter(course=course)
    return Response(serializers.DeliverableSerializer(deliverables, many=True).data)


@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@students_only
def get_student_deliverable_submissions_view(request):
    profile = models.Profile.objects.get(user=request.user)
    deliverable_submissions = models.DeliverableSubmission.objects.filter(submitter=profile)
    return Response(serializers.StudentDeliverableSubmissionSerializer(deliverable_submissions, many=True).data)


@api_view(['GET'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@professors_only
def get_professor_deliverables_submissions_view(request, deliverable_id):
    profile = models.Profile.objects.get(user=request.user)
    deliverable = models.Deliverable.objects.filter(pk=deliverable_id)

    # Check if deliverable submission id exists in db
    if not deliverable.exists():
        return Response({
            'error': f"Deliverable n°{deliverable_id} does not exist."
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if professor is professor of this course
    if deliverable.get().course.professor != profile:
        return Response({
            'error': 'Cannot view submissions for classes with a different professor'
        }, status=status.HTTP_403_FORBIDDEN)

    submissions = models.DeliverableSubmission.objects.filter(deliverable=deliverable.get())
    return Response(serializers.ProfessorDeliverableSubmissionSerializer(submissions, many=True).data)
