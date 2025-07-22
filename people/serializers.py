from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Teacher, Student
from .models import Exam, Question, ExamAssignment, StudentExamAttempt, StudentAnswer


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
    assigned_teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'phone_number', 'roll_number',
            'student_class', 'date_of_birth', 'admission_date',
            'status', 'username', 'password', 'email', 'user', 'assigned_teacher'
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
        if Student.objects.filter(roll_number=validated_data.get('roll_number')).exists():
            raise ValidationError({'roll_number': 'Roll number already exists.'})

        user = User.objects.create_user(username=username, password=password, email=email)
        validated_data['user'] = user
        return Student.objects.create(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Determine role based on user properties
        if user.is_superuser:
            role = 'admin'
        elif hasattr(user, 'teacher'):
            role = 'teacher'
        elif hasattr(user, 'student'):
            role = 'student'
        else:
            role = 'unknown'

        data['role'] = role
        data['username'] = user.username
        data['email'] = user.email

        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email.")
        return value
    

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'subject', 'date', 'duration', 'questions']

    def create(self, validated_data):
        teacher_user = validated_data.pop('teacher', None)
        if not teacher_user:
            request = self.context.get('request')
            teacher_user = request.user if request else None
        
        if not teacher_user or not hasattr(teacher_user, 'teacher'):
            raise serializers.ValidationError("Only teachers can create exams.")

        questions_data = validated_data.pop('questions',[])
        exam = Exam.objects.create(teacher=teacher_user, **validated_data)  # Assign User instance
        for question_data in questions_data:
            Question.objects.create(exam=exam, **question_data)
        return exam


class ExamAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAssignment
        fields = ['id', 'exam', 'student']


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['question', 'selected_option']


class StudentExamAttemptSerializer(serializers.ModelSerializer):
    answers = StudentAnswerSerializer(many=True, write_only=True)

    class Meta:
        model = StudentExamAttempt
        fields = ['exam', 'student', 'answers']
        read_only_fields = ['start_time', 'submitted', 'score']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        student = validated_data.pop('student', None)
        attempt = StudentExamAttempt.objects.create(student=student, **validated_data)
        for answer_data in answers_data:
            StudentAnswer.objects.create(attempt=attempt, **answer_data)
        return attempt