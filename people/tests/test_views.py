from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from people.models import Teacher, Student
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date


class BaseAPITestCase(APITestCase):
    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate(self, user):
        token = self.get_token_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class TeacherViewSetTests(BaseAPITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        self.client = APIClient()
        self.authenticate(self.admin_user)

    def test_create_teacher(self):
        payload = {
            'username': 'teach1',
            'password': 'teachpass',
            'email': 'teach1@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': 1234567890,
            'subject': 'Physics',
            'e_id': 'T100',
            'doj': '2023-01-01',
            'status': 'Active'
        }
        response = self.client.post('/people/teachers/', data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_teachers(self):
        response = self.client.get('/people/teachers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_export_teachers_csv(self):
        response = self.client.get('/people/export/teachers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')


class StudentViewSetTests(BaseAPITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='adminpass')
        self.teacher_user = User.objects.create_user(username='teacher1', password='teachpass')
        self.student_user = User.objects.create_user(username='student1', password='studpass')

        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='TFirst', last_name='TLast',
            email='t1@example.com', phone=1111111111,
            subject='Math', e_id='T001', doj='2023-01-01', status='Active'
        )

        self.student = Student.objects.create(
            user=self.student_user,
            first_name='SFirst', last_name='SLast',
            email='s1@example.com', phone_number='9999999999',
            roll_number='R001', student_class='10A',
            date_of_birth='2006-05-01', admission_date='2021-06-01',
            assigned_teacher=self.teacher,
            status='Active'
        )

        self.client = APIClient()

    def test_list_students_as_admin(self):
        self.authenticate(self.admin)
        res = self.client.get('/people/students/')
        self.assertEqual(res.status_code, 200)

    def test_list_students_as_teacher(self):
        self.authenticate(self.teacher_user)
        res = self.client.get('/people/students/')
        self.assertEqual(res.status_code, 200)

    def test_retrieve_student_as_teacher(self):
        self.authenticate(self.teacher_user)
        url = f'/people/students/{self.student.id}/'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_retrieve_student_forbidden(self):
        stranger = User.objects.create_user(username='stranger', password='1234')
        self.authenticate(stranger)
        url = f'/people/students/{self.student.id}/'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)  # Not 403, because student not in queryset

    def test_update_student_as_teacher(self):
        self.authenticate(self.teacher_user)
        url = f'/people/students/{self.student.id}/'
        res = self.client.patch(url, {'student_class': '10B'}, format='json')
        self.assertEqual(res.status_code, 200)

    def test_destroy_student_as_non_admin(self):
        self.authenticate(self.teacher_user)
        url = f'/people/students/{self.student.id}/'
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 403)

    def test_destroy_student_as_admin(self):
        self.authenticate(self.admin)
        url = f'/people/students/{self.student.id}/'
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 204)

    def test_student_me_endpoint(self):
        self.authenticate(self.student_user)
        res = self.client.get('/people/students/me/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['first_name'], 'SFirst')

    def test_students_by_teacher(self):
        self.authenticate(self.admin)
        res = self.client.get(f'/people/students/by-teacher/{self.teacher.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_export_students_csv(self):
        self.authenticate(self.admin)
        res = self.client.get('/people/export/students/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'text/csv')


class TeacherMeTest(BaseAPITestCase):  # ✅ inherit from BaseAPITestCase
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='teacher2', password='test123')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='Teach', last_name='Er',
            email='teach2@example.com', phone=1234567890,
            subject='Science', e_id='T202', doj='2022-01-01', status='Active'
        )
        self.client = APIClient()

    def test_teacher_me_endpoint(self):
        self.authenticate(self.teacher_user)
        res = self.client.get('/people/teachers/me/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['email'], 'teach2@example.com')


class AuthTokenTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='admin123', email='admin@example.com')

    def test_get_token_as_admin(self):
        res = self.client.post('/people/token/', {
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
