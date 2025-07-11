from django.test import TestCase
from django.contrib.auth.models import User
from people.models import Teacher, Student
from datetime import date

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='teacheruser')

    def test_teacher_str(self):
        teacher = Teacher.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone=1234567890,
            subject="Math",
            e_id="T123",
            doj="2023-01-01",
            status="Active"
        )
        self.assertEqual(str(teacher), "John Doe")

    def test_student_str(self):
        teacher = Teacher.objects.create(
            user=self.user,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone=9876543210,
            subject="Physics",
            e_id="T456",
            doj="2023-02-01",
            status="Active"
        )
        student = Student.objects.create(
            user=User.objects.create(username='studentuser'),
            first_name="Amy",
            last_name="Antony",
            email="amy@example.com",
            phone_number="9999999999",
            roll_number="R001",
            student_class="10A",
            date_of_birth="2010-01-01",
            admission_date="2023-06-01",
            status="Active",
            assigned_teacher=teacher
        )
        self.assertEqual(str(student), "Amy Antony")
