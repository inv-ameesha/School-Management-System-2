from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Teacher, Student


# 🔹 Teacher Serializer
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'


# 🔹 Student Serializer (with automatic User creation)
class StudentSerializer(serializers.ModelSerializer):
    # These fields are used to auto-create the User account
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'phone_number', 'roll_number',
            'student_class', 'date_of_birth', 'admission_date',
            'status', 'username', 'password', 'email', 'user'
        ]
        read_only_fields = ['user']  # Prevent manual setting from request

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')

        # Check for duplicate username/email in User model
        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'This username is already taken.'})
        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'This email is already registered.'})

        # Check for duplicate email and roll number in Student model
        if Student.objects.filter(email=email).exists():
            raise ValidationError({'email': 'This email is already used by another student.'})
        if Student.objects.filter(roll_number=validated_data.get('roll_number')).exists():
            raise ValidationError({'roll_number': 'This roll number already exists.'})

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email)

        # Create student and link user
        student = Student.objects.create(user=user, email=email, **validated_data)
        return student


# 🔹 Registration Serializer (for Admin to create any user)
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


# 🔐 Custom JWT Login Serializer with Role Validation
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        role = self.context['request'].data.get('role')

        if not role:
            raise AuthenticationFailed('Role is required.')

        data = super().validate(attrs)
        user = self.user

        # Role validation
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

        # Add user info to response
        data['role'] = role
        data['username'] = user.username
        data['email'] = user.email

        return data
