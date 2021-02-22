from rest_framework import serializers
from .models import Profile, Deliverable


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['name', 'user_type', 'program']


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    name = serializers.CharField(required=True, max_length=128)
    user_type = serializers.CharField(required=True, max_length=2)
    program = serializers.CharField(required=False, max_length=128)

    def validate(self, data):
        if 'user_type' not in data.keys():
            raise serializers.ValidationError('Field user_type is required.')

        if data['user_type'] == Profile.UserType.STUDENT and \
                ('program' not in data.keys() or len(data['program']) == 0):
            raise serializers.ValidationError("Field program is required.")

        if data['user_type'] == Profile.UserType.PROFESSOR and 'program' in data.keys():
            data['program'] = ''

        return super().validate(data)


class DeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliverable
        fields = '__all__'
