from django.test import TestCase
from django.contrib.auth.models import User
from people.models import Teacher, Student
from people.serializers import TeacherSerializer, StudentSerializer, RegisterSerializer
from rest_framework.exceptions import ValidationError

class TeacherSerializerValidationTest(TestCase):
    def setUp(self):
        self.existing_user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com'
        )

    def test_duplicate_username(self):
        data = {
            'username': 'testuser',  # Duplicate username
            'password': 'pass123',
            'email': 'newemail@example.com',
            'first_name': 'A',
            'last_name': 'B',
            'phone': 1234567890,
            'subject': 'Math',
            'e_id': 'T001',
            'doj': '2023-01-01',
            'status': 'Active'
        }
        serializer = TeacherSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(ValidationError) as context:
            serializer.save()
        self.assertIn("This username is already taken.", str(context.exception))

    def test_valid_teacher_creation(self):
        data = {
            'username': 'uniqueuser',
            'password': 'pass123',
            'email': 'unique@example.com',
            'first_name': 'A',
            'last_name': 'B',
            'phone': 9876543210,
            'subject': 'Science',
            'e_id': 'T002',
            'doj': '2023-02-01',
            'status': 'Active'
        }
        serializer = TeacherSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        teacher = serializer.save()
        self.assertEqual(teacher.user.username, 'uniqueuser')
        self.assertEqual(teacher.email, 'unique@example.com')


class RegisterSerializerTest(TestCase):
    def setUp(self):
        self.existing_user = User.objects.create_user(
            username='user1',
            email='duplicate@example.com',
            password='test'
        )

    def test_register_serializer_success(self):
        data = {
            'username': 'newuser',
            'password': 'newpass',
            'email': 'new@example.com'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')

    def test_duplicate_email(self):
        data = {
            'username': 'user2',
            'email': 'duplicate@example.com',
            'password': 'pass'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(ValidationError) as context:
            serializer.save()
        self.assertIn("Email already exists", str(context.exception))
