from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Teacher, Student,FeeStructure,StudentFee
from .models import Exam, Question, ExamAssignment, StudentExamAttempt, StudentAnswer


class TeacherSerializer(serializers.ModelSerializer):
    #external fields of user table
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = Teacher#model specified
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'subject',
            'e_id', 'doj', 'status', 'user',
            'username', 'password'
        ]
        read_only_fields = ['user', 'id']#auto assign user must not edit it

    def create(self, validated_data):
        #validated_data : dictionary which is auto created by rest framework,for create,update to store latest data
        #it is must in serializers else we need to fetch data like request.data which doesnot check for validation which extempts the usage of serailizers itself
        username = validated_data.pop('username')#pop done bcz its not a part of teacher model 
        password = validated_data.pop('password')
        email = validated_data.get('email')

        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'This username is already taken.'})
        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'This email is already registered.'})
        if Teacher.objects.filter(e_id=validated_data.get('e_id')).exists():
            raise ValidationError({'e_id': 'This e_id already exists.'})

        user = User.objects.create_user(username=username, password=password, email=email)
        validated_data['user'] = user#add the newly created teacher to the validated_data dictionary
        return Teacher.objects.create(**validated_data)#create teacher with username,pwd,email and all additional fields

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
    role = serializers.CharField(required=False)
    #TokenObtainPairSerializer : generates access token,refresh token
    #this function used when some credentials like role,user_id etc are passed other than access token,refresh token
    def validate(self, attrs):#inbuilt method, auto-called when username,pwd SUBMITTED BY USER
        data = super().validate(attrs)#validates to generate access token,refresh token
        user = self.user#find the authenticated user

        # Determine role based on user properties
        #since the teacher,student model has a onetoone relation btw teachertable and user table where user table inturn creates a user.teacher option too
        if user.is_superuser:
            real_role = 'admin'
        elif hasattr(user, 'teacher'):
            real_role = 'teacher'
        elif hasattr(user, 'student'):
            real_role = 'student'
        else:
            real_role = 'unknown'

        requested_role = self.initial_data.get('role')
        if requested_role and requested_role != real_role:
            raise serializers.ValidationError(f"Role mismatch: You are '{real_role}', not '{requested_role}'.")

        data['role'] = real_role#adds to data to be returned during token response
        data['username'] = user.username
        data['email'] = user.email

        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()#creates email field by validating it

    def validate_email(self, value):#custom validator for mail
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email.")
        return value
    

class PasswordResetConfirmSerializer(serializers.Serializer):
    #3 fields required for this
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)#write-only : only used as input,not exposed in response
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):#data:entered data
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def save(self):
        email = self.validated_data['email']#new pwd for pwd is set
        new_password = self.validated_data['new_password']
        user = User.objects.get(email=email)#finds the corresponding user from user table with that email
        user.set_password(new_password)
        user.save()

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)#we can create a list of questions with the same object

    class Meta:
        model = Exam
        fields = ['id', 'title', 'subject', 'date', 'duration', 'questions']

    def create(self, validated_data):
        teacher_user = validated_data.pop('teacher', None)#gets the teacher info from the validated_data
        #since we does not pass 'teacher' through our frontend it might not understand that its teacher
        if not teacher_user:
            request = self.context.get('request')#so we will first fetch the request
            teacher_user = request.user if request else None#then will fetch the user
        
        if not teacher_user or not hasattr(teacher_user, 'teacher'):
            raise serializers.ValidationError("Only teachers can create exams.")

        questions_data = validated_data.pop('questions',[])#each question entered stored to validated_data , only that qstns are popped out
        exam = Exam.objects.create(teacher=teacher_user, **validated_data)  #creates exam assign a user(teacher) to it
        for question_data in questions_data:
            Question.objects.create(exam=exam, **question_data)#using all the questions created it will create an exam
        return exam


class ExamAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAssignment
        fields = ['id', 'exam', 'student']

#ensures that student valid answer only received 
class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['question', 'selected_option']

#students submit entire exam with all answers
class StudentExamAttemptSerializer(serializers.ModelSerializer):
    answers = StudentAnswerSerializer(many=True, write_only=True)

    class Meta:
        model = StudentExamAttempt
        fields = ['exam', 'student', 'answers']
        read_only_fields = ['start_time', 'submitted', 'score']#not to be passed by the frontend,auto assigned

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')#fetch each answer individually
        student = validated_data.pop('student', None)#fetch corresponding student also
        attempt = StudentExamAttempt.objects.create(student=student, **validated_data)#create an attempt
        for answer_data in answers_data:
            StudentAnswer.objects.create(attempt=attempt, **answer_data)#save all the answers to this attempt
        return attempt

class FeeAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = ['grade', 'academic_year', 'base_fee', 'due_date', 'fine_per_day']

    def validate(self, data):
        if FeeStructure.objects.filter(
            grade=data['grade'],
            academic_year=data['academic_year']
        ).exists():
            raise serializers.ValidationError(
                "Fee structure already exists for this class and academic year."
            )
        return data

    def create(self, validated_data):
        fee_structure = FeeStructure.objects.create(**validated_data)

        students = Student.objects.filter(grade=fee_structure.grade, status="active")

        student_fees = [
            StudentFee(
                student=student,
                fee_structure=fee_structure,
                total_amount=fee_structure.base_fee,
                due_date=fee_structure.due_date,
                status="pending"
            )
            for student in students
        ]
        StudentFee.objects.bulk_create(student_fees)

        return fee_structure
