from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Teacher, Student

class TeacherSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'subject',
            'e_id', 'doj', 'status', 'user',
            'username', 'password'
        ]
        read_only_fields = ['user', 'id']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.get('email')

        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'This username is already taken.'})
        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'This email is already registered.'})
        if Teacher.objects.filter(e_id=validated_data.get('e_id')).exists():
            raise ValidationError({'e_id': 'This e_id already exists.'})

        user = User.objects.create_user(username=username, password=password, email=email)
        validated_data['user'] = user
        return Teacher.objects.create(**validated_data)
class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'phone_number', 'roll_number',
            'student_class', 'date_of_birth', 'admission_date',
            'status', 'username', 'password', 'email', 'user', 'assigned_teacher'
        ]
        read_only_fields = ['user', 'id', 'assigned_teacher']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.get('email')

        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'This username is already taken.'})
        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'This email is already registered.'})
        if Student.objects.filter(roll_number=validated_data.get('roll_number')).exists():
            raise ValidationError({'roll_number': 'Roll number already exists.'})

        user = User.objects.create_user(username=username, password=password, email=email)
        validated_data['user'] = user
        return Student.objects.create(**validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if User.objects.filter(username=validated_data['username']).exists():
            raise ValidationError({'username': 'Username already exists'})
        if User.objects.filter(email=validated_data['email']).exists():
            raise ValidationError({'email': 'Email already exists'})
        return User.objects.create_user(**validated_data)


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
