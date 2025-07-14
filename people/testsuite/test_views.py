from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from people.models import Teacher, Student, Exam, ExamAssignment, StudentExamAttempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import make_aware, now
from datetime import datetime, timedelta
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import csv
import io
from django.utils import timezone
import json

class BaseAPITestCase(APITestCase):
    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate(self, user):
        token = self.get_token_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class ExamFlowTests(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()

    
        self.teacher_user = User.objects.create_user(username='teacher', password='pass')
        self.student_user = User.objects.create_user(username='student', password='pass')

        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='T', last_name='One',
            email='teacher@example.com', phone=111,
            subject='Math', e_id='T001',
            doj='2023-01-01', status='Active'
        )

        self.student = Student.objects.create(
            user=self.student_user,
            first_name='S', last_name='One',
            email='student@example.com', phone_number='99999',
            roll_number='R001', student_class='10A',
            date_of_birth='2006-05-01', admission_date='2021-06-01',
            assigned_teacher=self.teacher, status='Active'
        )

        
        self.authenticate(self.teacher_user)
        self.exam_response = self.client.post('/people/exams/create/', {
            "title": "Maths Test",
            "subject": "Math",
            "date": "2025-01-01",
            "duration": 300,
            "questions": [
                {
                    "text": "What is 2+2?",
                    "option_a": "3", "option_b": "4",
                    "option_c": "5", "option_d": "6",
                    "correct_option": "b"
                }
            ]
        }, format='json')

        assert self.exam_response.status_code == 201, f"Exam creation failed: {self.exam_response.content}"
        self.exam_id = self.exam_response.data['id']
        self.exam = Exam.objects.get(id=self.exam_id)

    def test_teacher_assign_exam_to_student(self):
        response = self.client.post('/people/exams/assign/', {
            "exam": self.exam_id,
            "students": [self.student_user.id]
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Exam assigned successfully')

    def test_student_start_exam(self):

        ExamAssignment.objects.create(exam=self.exam, student=self.student_user)
        self.authenticate(self.student_user)

    
        self.client.get(f'/people/exams/{self.exam_id}/attempt/')

   
        attempt = StudentExamAttempt.objects.get(exam=self.exam, student=self.student_user)
        attempt.started_at = timezone.now() - timedelta(seconds=self.exam.duration + 10)
        attempt.save()

    
        response = self.client.get(f'/people/exams/{self.exam_id}/attempt/')

        self.assertEqual(response.status_code, 403)
        self.assertIn('Exam time expired', response.data.get('error', ''))

    def test_student_submit_exam_score(self):
        ExamAssignment.objects.create(exam=self.exam, student=self.student_user)
        self.authenticate(self.student_user)
        StudentExamAttempt.objects.create(student=self.student_user, exam=self.exam, started_at=now())

        response = self.client.post(f'/people/exams/{self.exam_id}/attempt/', {
            'score': 5
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Exam submitted successfully')

    def test_exam_submission_after_time_expiry(self):
        ExamAssignment.objects.create(exam=self.exam, student=self.student_user)
        self.authenticate(self.student_user)
        
        
        attempt = StudentExamAttempt.objects.create(
            student=self.student_user,
            exam=self.exam
        )
       
        past_time = now() - timedelta(seconds=self.exam.duration + 10)
        attempt.started_at = past_time
        attempt.save()

        response = self.client.post(f'/people/exams/{self.exam_id}/attempt/', {'score': 10})
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        print(f"Exam duration: {self.exam.duration}")
        print(f"Time elapsed: {(now() - attempt.started_at).total_seconds()}")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], 'Exam time expired')

    def test_exam_attempt_twice_prevented(self):
        ExamAssignment.objects.create(exam=self.exam, student=self.student_user)
        self.authenticate(self.student_user)

        self.client.get(f'/people/exams/{self.exam_id}/attempt/')

        attempt = StudentExamAttempt.objects.get(exam=self.exam, student=self.student_user)
        attempt.started_at = timezone.now() - timedelta(seconds=self.exam.duration + 10)
        attempt.save()

        res = self.client.get(f'/people/exams/{self.exam_id}/attempt/')

        self.assertEqual(res.status_code, 403)

        error_data = json.loads(res.content)
        self.assertIn('Exam time expired', error_data.get('error', ''))


class AssignedExamsViewTest(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()

        self.teacher_user = User.objects.create_user(username='teacher', password='pass')
        self.student_user = User.objects.create_user(username='student', password='pass')

        self.teacher = Teacher.objects.create(
            user=self.teacher_user, first_name='T', last_name='Teach',
            email='teacher@example.com', phone=123,
            subject='Physics', e_id='T999', doj='2023-02-01', status='Active'
        )

        self.exam = Exam.objects.create(
            title="Science Test", subject="Science",
            date="2025-01-01", duration=60,
            teacher=self.teacher_user
        )

        ExamAssignment.objects.create(exam=self.exam, student=self.student_user)

    def test_student_assigned_exam_list(self):
        self.authenticate(self.student_user)
        res = self.client.get('/people/exams/assigned/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


class TeacherViewSetTests(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
        self.teacher_user = User.objects.create_user(username='teacher', password='pass')
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John', last_name='Doe',
            email='john@example.com', phone=1234567890,
            subject='Math', e_id='T001',
            doj='2023-01-01', status='Active'
        )

    def test_teacher_list_admin_access(self):
        self.authenticate(self.admin_user)
        response = self.client.get('/people/teachers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_teacher_list_non_admin_denied(self):
        self.authenticate(self.teacher_user)
        response = self.client.get('/people/teachers/')
        self.assertEqual(response.status_code, 403)

    def test_teacher_detail_admin_access(self):
        self.authenticate(self.admin_user)
        response = self.client.get(f'/people/teachers/{self.teacher.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'John')

    def test_teacher_create_admin_access(self):
        self.authenticate(self.admin_user)
        data = {
            'username': 'newteacher',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone': 9876543210,
            'subject': 'Physics',
            'e_id': 'T002',
            'doj': '2023-02-01',
            'status': 'Active'
        }
        response = self.client.post('/people/teachers/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Teacher.objects.count(), 2)

    def test_teacher_update_admin_access(self):
        self.authenticate(self.admin_user)
        data = {'first_name': 'Updated Name'}
        response = self.client.patch(f'/people/teachers/{self.teacher.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.first_name, 'Updated Name')

    def test_teacher_delete_admin_access(self):
        self.authenticate(self.admin_user)
        response = self.client.delete(f'/people/teachers/{self.teacher.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Teacher.objects.count(), 0)

    def test_teacher_me_endpoint(self):
        self.authenticate(self.teacher_user)
        response = self.client.get('/people/teachers/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'John')


class StudentViewSetTests(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
        self.teacher_user = User.objects.create_user(username='teacher', password='pass')
        self.student_user = User.objects.create_user(username='student', password='pass')
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John', last_name='Doe',
            email='john@example.com', phone=1234567890,
            subject='Math', e_id='T001',
            doj='2023-01-01', status='Active'
        )
        
        self.student = Student.objects.create(
            user=self.student_user,
            first_name='Jane', last_name='Smith',
            email='jane@example.com', phone_number='9876543210',
            roll_number='R001', student_class='10A',
            date_of_birth='2008-01-01', admission_date='2023-06-01',
            assigned_teacher=self.teacher, status='Active'
        )

    def test_student_list_admin_access(self):
        self.authenticate(self.admin_user)
        response = self.client.get('/people/students/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_student_list_teacher_access(self):
        self.authenticate(self.teacher_user)
        response = self.client.get('/people/students/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_student_list_student_denied(self):
        self.authenticate(self.student_user)
        response = self.client.get('/people/students/')
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(len(response.data), 1)

    def test_student_detail_admin_access(self):
        self.authenticate(self.admin_user)
        response = self.client.get(f'/people/students/{self.student.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'Jane')

    def test_student_create_admin_access(self):
        self.authenticate(self.admin_user)
        data = {
            'username': 'newstudent',
            'password': 'password123',
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'email': 'bob@example.com',
            'phone_number': '1234567890',
            'roll_number': 'R002',
            'student_class': '10B',
            'date_of_birth': '2008-02-01',
            'admission_date': '2023-06-01',
            'assigned_teacher': self.teacher.id,
            'status': 'Active'
        }
        response = self.client.post('/people/students/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Student.objects.count(), 2)

    def test_student_update_admin_access(self):
        self.authenticate(self.admin_user)
        data = {'first_name': 'Updated Name'}
        response = self.client.patch(f'/people/students/{self.student.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, 'Updated Name')

    def test_student_delete_admin_access(self):
        self.authenticate(self.admin_user)
        response = self.client.delete(f'/people/students/{self.student.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Student.objects.count(), 0)

    def test_student_me_endpoint(self):
        self.authenticate(self.student_user)
        response = self.client.get('/people/students/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'Jane')

    def test_student_by_teacher_endpoint(self):
        
        admin_user = User.objects.create_user(username='adminuser', password='pass', is_superuser=True, is_staff=True)
        self.authenticate(admin_user)
        response = self.client.get(f'/people/students/by-teacher/{self.teacher.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class RegisterViewTests(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')

    def test_register_user_admin_access(self):
        self.authenticate(self.admin_user)
        data = {
            'username': 'newuser',
            'password': 'password123',
            'email': 'newuser@example.com'
        }
        response = self.client.post('/people/register/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 2)

    def test_register_user_non_admin_denied(self):
        regular_user = User.objects.create_user(username='regular', password='pass')
        self.authenticate(regular_user)
        data = {
            'username': 'newuser',
            'password': 'password123',
            'email': 'newuser@example.com'
        }
        response = self.client.post('/people/register/', data, format='json')
        self.assertEqual(response.status_code, 403)


class CSVExportTests(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
        
        self.teacher_user = User.objects.create_user(username='teacher', password='pass')
        self.student_user = User.objects.create_user(username='student', password='pass')
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John', last_name='Doe',
            email='john@example.com', phone=1234567890,
            subject='Math', e_id='T001',
            doj='2023-01-01', status='Active'
        )
        
        self.student = Student.objects.create(
            user=self.student_user,
            first_name='Jane', last_name='Smith',
            email='jane@example.com', phone_number='9876543210',
            roll_number='R001', student_class='10A',
            date_of_birth='2008-01-01', admission_date='2023-06-01',
            assigned_teacher=self.teacher, status='Active'
        )

    def test_export_students_csv_admin_access(self):
        self.authenticate(self.admin_user)
        response = self.client.get('/people/export/students/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_export_teachers_csv_admin_access(self):
        self.authenticate(self.admin_user)
        response = self.client.get('/people/export/teachers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_export_students_csv_non_admin_denied(self):
        regular_user = User.objects.create_user(username='regular', password='pass')
        self.authenticate(regular_user)
        response = self.client.get('/people/export/students/')
        self.assertEqual(response.status_code, 403)

    def test_export_teachers_csv_non_admin_denied(self):
        regular_user = User.objects.create_user(username='regular', password='pass')
        self.authenticate(regular_user)
        response = self.client.get('/people/export/teachers/')
        self.assertEqual(response.status_code, 403)


class CSVImportTests(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
        
        self.teacher_user = User.objects.create_user(username='teacher', password='pass')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John', last_name='Doe',
            email='john@example.com', phone=1234567890,
            subject='Math', e_id='T001',
            doj='2023-01-01', status='Active'
        )

    def test_import_students_csv_admin_access(self):
        self.authenticate(self.admin_user)
        
        
        csv_content = "username,password,email,first_name,last_name,phone_number,roll_number,student_class,date_of_birth,admission_date,status,assigned_teacher_id\n"
        csv_content += "newstudent,pass123,new@example.com,New,Student,1234567890,R002,10B,2008-01-01,2023-06-01,Active,1\n"
        
        csv_file = SimpleUploadedFile("students.csv", csv_content.encode('utf-8'), content_type="text/csv")
        
        response = self.client.post('/people/import/students/', {'file': csv_file})
        self.assertEqual(response.status_code, 201)
        self.assertIn('imported successfully', response.data['message'])

    def test_import_students_csv_invalid_format(self):
        self.authenticate(self.admin_user)
        
        
        invalid_file = SimpleUploadedFile("students.txt", b"invalid content", content_type="text/plain")
        
        response = self.client.post('/people/import/students/', {'file': invalid_file})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid file format', response.data['error'])

    def test_import_students_csv_non_admin_denied(self):
        regular_user = User.objects.create_user(username='regular', password='pass')
        self.authenticate(regular_user)
        
        csv_file = SimpleUploadedFile("students.csv", b"test", content_type="text/csv")
        response = self.client.post('/people/import/students/', {'file': csv_file})
        self.assertEqual(response.status_code, 403)


class PasswordResetTests(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='oldpass')

    def test_password_reset_request_valid_email(self):
        response = self.client.post('/people/password-reset/', {
            'email': 'test@example.com'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Password reset link sent', response.data['message'])

    def test_password_reset_request_invalid_email(self):
        response = self.client.post('/people/password-reset/', {
            'email': 'nonexistent@example.com'
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_valid(self):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator
        
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        response = self.client.post(f'/people/password-reset/confirm/{uid}/{token}/', {
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Password has been reset', response.data['message'])

    def test_password_reset_confirm_mismatch_passwords(self):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator
        
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        response = self.client.post(f'/people/password-reset/confirm/{uid}/{token}/', {
            'new_password': 'newpass123',
            'confirm_password': 'differentpass'
        }, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Passwords do not match', response.data['error'])

    def test_password_reset_confirm_missing_passwords(self):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator
        
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        response = self.client.post(f'/people/password-reset/confirm/{uid}/{token}/', {
            'new_password': 'newpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Both password fields are required', response.data['error'])

    def test_password_reset_confirm_invalid_token(self):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        invalid_token = 'invalid-token'
        
        response = self.client.post(f'/people/password-reset/confirm/{uid}/{invalid_token}/', {
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Token is invalid or expired', response.data['error'])


class ExamAssignmentViewTests(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher_user = User.objects.create_user(username='teacher', password='pass')
        self.student_user = User.objects.create_user(username='student', password='pass')
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John', last_name='Doe',
            email='john@example.com', phone=1234567890,
            subject='Math', e_id='T001',
            doj='2023-01-01', status='Active'
        )
        
        self.student = Student.objects.create(
            user=self.student_user,
            first_name='Jane', last_name='Smith',
            email='jane@example.com', phone_number='9876543210',
            roll_number='R001', student_class='10A',
            date_of_birth='2008-01-01', admission_date='2023-06-01',
            assigned_teacher=self.teacher, status='Active'
        )
        
        self.exam = Exam.objects.create(
            title="Test Exam", subject="Math",
            date="2025-01-01", duration=60,
            teacher=self.teacher_user
        )

    def test_assign_exam_success(self):
        self.authenticate(self.teacher_user)
        response = self.client.post('/people/exams/assign/', {
            'exam': self.exam.id,
            'students': [self.student_user.id]
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('assigned successfully', response.data['message'])

    def test_assign_exam_wrong_teacher(self):
       
        other_teacher_user = User.objects.create_user(username='otherteacher', password='pass')
        other_teacher = Teacher.objects.create(
            user=other_teacher_user,
            first_name='Other', last_name='Teacher',
            email='other@example.com', phone=1234567890,
            subject='Physics', e_id='T002',
            doj='2023-01-01', status='Active'
        )
        
        
        other_exam = Exam.objects.create(
            title="Other Exam", subject="Physics",
            date="2025-01-01", duration=60,
            teacher=other_teacher_user
        )
        
        self.authenticate(self.teacher_user)
        response = self.client.post('/people/exams/assign/', {
            'exam': other_exam.id,
            'students': [self.student_user.id]
        }, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('assigned successfully', response.data['message'])

    def test_assign_exam_not_found(self):
        self.authenticate(self.teacher_user)
        response = self.client.post('/people/exams/assign/', {
            'exam': 99999,
            'students': [self.student_user.id]
        }, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertIn('Exam not found', response.data['error'])

    def test_assign_exam_student_not_found(self):
        self.authenticate(self.teacher_user)
        response = self.client.post('/people/exams/assign/', {
            'exam': self.exam.id,
            'students': [99999]
        }, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertIn('Student with id 99999 not found', response.data['error'])


class AttemptExamViewTests(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher_user = User.objects.create_user(username='teacher', password='pass')
        self.student_user = User.objects.create_user(username='student', password='pass')
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John', last_name='Doe',
            email='john@example.com', phone=1234567890,
            subject='Math', e_id='T001',
            doj='2023-01-01', status='Active'
        )
        
        self.student = Student.objects.create(
            user=self.student_user,
            first_name='Jane', last_name='Smith',
            email='jane@example.com', phone_number='9876543210',
            roll_number='R001', student_class='10A',
            date_of_birth='2008-01-01', admission_date='2023-06-01',
            assigned_teacher=self.teacher, status='Active'
        )
        
        self.exam = Exam.objects.create(
            title="Test Exam", subject="Math",
            date="2025-01-01", duration=60,
            teacher=self.teacher_user
        )

    def test_attempt_exam_not_assigned(self):
        self.authenticate(self.student_user)
        response = self.client.get(f'/people/exams/{self.exam.id}/attempt/')
        self.assertEqual(response.status_code, 403)
        self.assertIn('Not assigned to this exam', response.data['error'])

    def test_attempt_exam_not_found(self):
        self.authenticate(self.student_user)
        response = self.client.get('/people/exams/99999/attempt/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Exam not found', response.data['error'])

    def test_submit_exam_no_score(self):
        ExamAssignment.objects.create(exam=self.exam, student=self.student_user)
        StudentExamAttempt.objects.create(student=self.student_user, exam=self.exam, started_at=now())
        
        self.authenticate(self.student_user)
        response = self.client.post(f'/people/exams/{self.exam.id}/attempt/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Score not provided', response.data['error'])

    def test_submit_exam_invalid_exam(self):
        self.authenticate(self.student_user)
        response = self.client.post('/people/exams/99999/attempt/', {'score': 10}, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Invalid exam or attempt', response.data['error'])

    def test_submit_exam_no_attempt(self):
        ExamAssignment.objects.create(exam=self.exam, student=self.student_user)
        
        self.authenticate(self.student_user)
        response = self.client.post(f'/people/exams/{self.exam.id}/attempt/', {'score': 10}, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Invalid exam or attempt', response.data['error'])
