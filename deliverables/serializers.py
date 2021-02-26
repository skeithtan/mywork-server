from rest_framework import serializers
from . import models


class ProfileSerializer(serializers.ModelSerializer):
    email_address = serializers.SerializerMethodField()

    def get_email_address(self, obj):
        return obj.user.username

    class Meta:
        model = models.Profile
        fields = ['id', 'name', 'user_type', 'program', 'email_address']


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    

    def validate(self, data):
        if 'email' not in data.keys():
            raise serializers.ValidationError('Field email is required.')
        if 'password' not in data.keys():
            raise serializers.ValidationError('Field password is required.')

        return super().validate(data)



class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    name = serializers.CharField(required=True, max_length=128)
    user_type = serializers.CharField(required=True, max_length=2)
    program = serializers.CharField(required=False, max_length=128)

    def validate(self, data):
        if 'user_type' not in data.keys():
            raise serializers.ValidationError('Field user_type is required.')

        if data['user_type'] == models.Profile.UserType.STUDENT and \
                ('program' not in data.keys() or len(data['program']) == 0):
            raise serializers.ValidationError("Field program is required.")

        if data['user_type'] == models.Profile.UserType.PROFESSOR and 'program' in data.keys():
            data['program'] = ''

        return super().validate(data)


class DeliverableSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()

    def get_course_name(self, obj):
        return obj.course.name

    class Meta:
        model = models.Deliverable
        fields = '__all__'


class StudentDeliverableSubmissionSerializer(serializers.ModelSerializer):
    deliverable = DeliverableSerializer()

    class Meta:
        model = models.DeliverableSubmission
        fields = '__all__'


class ProfessorDeliverableSubmissionSerializer(serializers.ModelSerializer):
    submitter = ProfileSerializer()
    group_members = ProfileSerializer(many=True)

    class Meta:
        model = models.DeliverableSubmission
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    professor = ProfileSerializer(read_only=True)
    students = ProfileSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = models.Course
        fields = '__all__'

class LinkAttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.LinkAttachment
        fields = '__all__'
