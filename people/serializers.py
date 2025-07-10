from rest_framework import serializers
from .models import Teacher, Student
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Teacher, Student

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

# Registration Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        role = self.context['request'].data.get('role')

        if not role:
            raise AuthenticationFailed('Role is required.')

        data = super().validate(attrs)
        user = self.user

        if role == 'admin':
            if not user.is_superuser:
                raise AuthenticationFailed('This user is not an admin.')
        elif role == 'teacher':
            if not Teacher.objects.filter(user=user).exists():
                raise AuthenticationFailed('This user is not a teacher.')
        elif role == 'student':
            if not Student.objects.filter(user=user).exists():
                raise AuthenticationFailed('This user is not a student.')
        else:
            raise AuthenticationFailed('Invalid role provided.')

        data['role'] = role
        data['username'] = user.username
        data['email'] = user.email

        return data