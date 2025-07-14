from django.test import TestCase
from django.contrib.auth.models import User
from people.models import (
    Teacher, Student, Exam, Question,
    ExamAssignment, StudentExamAttempt, StudentAnswer
)
from people.serializers import (
    TeacherSerializer, StudentSerializer, RegisterSerializer,
    CustomTokenObtainPairSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, ExamSerializer, StudentExamAttemptSerializer
)
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from datetime import date

class SerializerTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.teacher_user = User.objects.create_user(
            username='teach1', email='t1@example.com', password='pass123'
        )
        self.student_user = User.objects.create_user(
            username='stud1', email='s1@example.com', password='pass123'
        )

        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name="T",
            last_name="One",
            email="t1@example.com",
            phone=1111111111,
            subject="Math",
            e_id="T001",
            doj="2023-01-01",
            status="Active"
        )

        self.student = Student.objects.create(
            user=self.student_user,
            first_name="S",
            last_name="One",
            email="s1@example.com",
            phone_number="1234567890",
            roll_number="R001",
            student_class="10A",
            date_of_birth="2010-01-01",
            admission_date="2023-06-01",
            status="Active",
            assigned_teacher=self.teacher
        )

    def test_teacher_serializer_valid(self):
        data = {
            "username": "newteacher",
            "password": "strongpass",
            "first_name": "Alice",
            "last_name": "Bob",
            "email": "alice@example.com",
            "phone": 1234567890,
            "subject": "Physics",
            "e_id": "T999",
            "doj": "2024-01-01",
            "status": "Active"
        }
        request = self.factory.post('/people/register/teacher/', data, format='json')
        request.user = self.teacher_user
        serializer = TeacherSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        teacher = serializer.save()
        self.assertEqual(teacher.first_name, "Alice")

    def test_teacher_serializer_duplicate_username(self):
        data = {
            "username": "teach1",  
            "password": "strongpass",
            "first_name": "Alice",
            "last_name": "Bob",
            "email": "alice2@example.com",
            "phone": 1234567890,
            "subject": "Physics",
            "e_id": "T999",
            "doj": "2024-01-01",
            "status": "Active"
        }
        request = self.factory.post('/people/register/teacher/', data, format='json')
        request.user = self.teacher_user
        serializer = TeacherSerializer(data=data, context={'request': request})
        
        serializer.is_valid()
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_teacher_serializer_duplicate_email(self):
        data = {
            "username": "newteacher",
            "password": "strongpass",
            "first_name": "Alice",
            "last_name": "Bob",
            "email": "t1@example.com",  
            "phone": 1234567890,
            "subject": "Physics",
            "e_id": "T999",
            "doj": "2024-01-01",
            "status": "Active"
        }
        request = self.factory.post('/people/register/teacher/', data, format='json')
        request.user = self.teacher_user
        serializer = TeacherSerializer(data=data, context={'request': request})
        
        serializer.is_valid()
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_teacher_serializer_duplicate_e_id(self):
        data = {
            "username": "newteacher",
            "password": "strongpass",
            "first_name": "Alice",
            "last_name": "Bob",
            "email": "alice@example.com",
            "phone": 1234567890,
            "subject": "Physics",
            "e_id": "T001",  
            "doj": "2024-01-01",
            "status": "Active"
        }
        request = self.factory.post('/people/register/teacher/', data, format='json')
        request.user = self.teacher_user
        serializer = TeacherSerializer(data=data, context={'request': request})
        
        self.assertFalse(serializer.is_valid())
        self.assertIn("e_id", serializer.errors)

    def test_student_serializer_duplicate_roll(self):
        data = {
            "username": "sduplicate",
            "password": "pass",
            "first_name": "Dup",
            "last_name": "Stu",
            "email": "dup@example.com",
            "phone_number": "9999999999",
            "roll_number": "R001",  
            "student_class": "10B",
            "date_of_birth": "2010-01-01",
            "admission_date": "2023-06-01",
            "status": "Active"
        }
        request = self.factory.post('/people/register/student/', data, format='json')
        request.user = self.teacher_user
        serializer = StudentSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("roll_number", serializer.errors)

    def test_student_serializer_duplicate_username(self):
        data = {
            "username": "stud1",  
            "password": "pass",
            "first_name": "Dup",
            "last_name": "Stu",
            "email": "dup@example.com",
            "phone_number": "9999999999",
            "roll_number": "R999",
            "student_class": "10B",
            "date_of_birth": "2010-01-01",
            "admission_date": "2023-06-01",
            "status": "Active"
        }
        request = self.factory.post('/people/register/student/', data, format='json')
        request.user = self.teacher_user
        serializer = StudentSerializer(data=data, context={'request': request})
        
        serializer.is_valid()
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_student_serializer_duplicate_email(self):
        data = {
            "username": "sduplicate",
            "password": "pass",
            "first_name": "Dup",
            "last_name": "Stu",
            "email": "s1@example.com",  
            "phone_number": "9999999999",
            "roll_number": "R999",
            "student_class": "10B",
            "date_of_birth": "2010-01-01",
            "admission_date": "2023-06-01",
            "status": "Active"
        }
        request = self.factory.post('/people/register/student/', data, format='json')
        request.user = self.teacher_user
        serializer = StudentSerializer(data=data, context={'request': request})
        
        serializer.is_valid()
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_register_serializer(self):
        data = {"username": "newuser", "password": "newpass", "email": "new@example.com"}
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.username, "newuser")

    def test_register_serializer_duplicate_username(self):
        data = {"username": "teach1", "password": "newpass", "email": "new@example.com"}
        serializer = RegisterSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_register_serializer_duplicate_email(self):
        data = {"username": "newuser", "password": "newpass", "email": "t1@example.com"}
        serializer = RegisterSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_custom_token_teacher_success(self):
        
        request = self.factory.post('/people/token/')
        drf_request = Request(request)
        
        drf_request._data = {'role': 'teacher'}
        
        drf_request._full_data = {'role': 'teacher'}

        serializer = CustomTokenObtainPairSerializer(
            data={'username': 'teach1', 'password': 'pass123'},
            context={'request': drf_request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['role'], 'teacher')

    def test_custom_token_student_success(self):
        request = self.factory.post('/people/token/')
        drf_request = Request(request)
        drf_request._data = {'role': 'student'}
        drf_request._full_data = {'role': 'student'}

        serializer = CustomTokenObtainPairSerializer(
            data={'username': 'stud1', 'password': 'pass123'},
            context={'request': drf_request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['role'], 'student')

    def test_custom_token_admin_success(self):
        admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='admin123'
        )
        request = self.factory.post('/people/token/')
        drf_request = Request(request)
        drf_request._data = {'role': 'admin'}
        drf_request._full_data = {'role': 'admin'}

        serializer = CustomTokenObtainPairSerializer(
            data={'username': 'admin', 'password': 'admin123'},
            context={'request': drf_request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['role'], 'admin')

    def test_custom_token_no_role(self):
        request = self.factory.post('/people/token/')
        drf_request = Request(request)
        drf_request._data = {}
        drf_request._full_data = {}

        serializer = CustomTokenObtainPairSerializer(
            data={'username': 'teach1', 'password': 'pass123'},
            context={'request': drf_request}
        )
        with self.assertRaises(Exception):
            serializer.is_valid()

    def test_custom_token_invalid_role(self):
        request = self.factory.post('/people/token/')
        drf_request = Request(request)
        drf_request._data = {'role': 'invalid'}
        drf_request._full_data = {'role': 'invalid'}

        serializer = CustomTokenObtainPairSerializer(
            data={'username': 'teach1', 'password': 'pass123'},
            context={'request': drf_request}
        )
        with self.assertRaises(Exception):
            serializer.is_valid()

    def test_custom_token_wrong_role_teacher(self):
        request = self.factory.post('/people/token/')
        drf_request = Request(request)
        drf_request._data = {'role': 'student'}
        drf_request._full_data = {'role': 'student'}

        serializer = CustomTokenObtainPairSerializer(
            data={'username': 'teach1', 'password': 'pass123'},
            context={'request': drf_request}
        )
        with self.assertRaises(Exception):
            serializer.is_valid()

    def test_password_reset_email_invalid(self):
        data = {'email': 'noone@example.com'}
        serializer = PasswordResetRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_password_reset_email_valid(self):
        data = {'email': 't1@example.com'}
        serializer = PasswordResetRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_password_reset_confirm_success(self):
        user = User.objects.create_user(username='resetuser', email='reset@example.com', password='oldpass')
        data = {
            "email": "reset@example.com",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        user.refresh_from_db()
        self.assertTrue(user.check_password("newpass123"))

    def test_password_reset_confirm_mismatch(self):
        user = User.objects.create_user(username='resetuser', email='reset@example.com', password='oldpass')
        data = {
            "email": "reset@example.com",
            "new_password": "newpass123",
            "confirm_password": "differentpass"
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_exam_with_questions_create(self):
        data = {
            "title": "Math Exam",
            "subject": "Math",
            "date": "2025-01-01",
            "duration": 60,
            "questions": [
                {
                    "text": "Q1",
                    "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
                    "correct_option": "a"
                }
            ]
        }
        request = self.factory.post('/people/exam/create/', data, format='json')
        request.user = self.teacher_user  
        serializer = ExamSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        exam = serializer.save()
        self.assertEqual(exam.title, "Math Exam")
        self.assertEqual(exam.questions.count(), 1)

    def test_exam_create_not_teacher(self):
        data = {
            "title": "Math Exam",
            "subject": "Math",
            "date": "2025-01-01",
            "duration": 60,
            "questions": [
                {
                    "text": "Q1",
                    "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
                    "correct_option": "a"
                }
            ]
        }
        request = self.factory.post('/people/exam/create/', data, format='json')
        request.user = self.student_user  
        serializer = ExamSerializer(data=data, context={'request': request})
        
        serializer.is_valid()
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_exam_attempt_with_answers(self):
        exam = Exam.objects.create(
            title="Test", subject="Sub",
            date="2025-01-01", duration=60,
            teacher=self.teacher_user  
        )
        q1 = Question.objects.create(
            exam=exam,
            text="Q?",
            option_a="A", option_b="B",
            option_c="C", option_d="D",
            correct_option="a"
        )

        data = {
            "exam": exam.id,
            "answers": [
                {"question": q1.id, "selected_option": "A"}
            ]
        }

        request = self.factory.post(f'/people/attempt-exam/{exam.id}/', data, format='json')
        request.user = self.student_user
        serializer = StudentExamAttemptSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        attempt = serializer.save(student=self.student_user)
        self.assertEqual(attempt.answers.count(), 1)

    def test_exam_attempt_with_student_object(self):
        exam = Exam.objects.create(
            title="Test", subject="Sub",
            date="2025-01-01", duration=60,
            teacher=self.teacher_user
        )
        q1 = Question.objects.create(
            exam=exam,
            text="Q?",
            option_a="A", option_b="B",
            option_c="C", option_d="D",
            correct_option="a"
        )

        data = {
            "exam": exam.id,
            "answers": [
                {"question": q1.id, "selected_option": "A"}
            ]
        }

        request = self.factory.post(f'/people/attempt-exam/{exam.id}/', data, format='json')
        request.user = self.student_user
        serializer = StudentExamAttemptSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        attempt = serializer.save(student=self.student)
        self.assertEqual(attempt.answers.count(), 1)
