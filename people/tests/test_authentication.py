from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from people.models import Teacher
from rest_framework_simplejwt.tokens import RefreshToken

class AuthTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teacher1', password='pass', email='t@example.com')
        self.teacher = Teacher.objects.create(user=self.user, first_name='T', last_name='One', email='t@example.com', phone=123, subject='Math', e_id='T200', doj='2023-01-01', status='Active')

    def test_valid_teacher_token(self):
        response = self.client.post('/people/token/', {
            'username': 'teacher1',
            'password': 'pass',
            'role': 'teacher'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_missing_role(self):
        response = self.client.post('/people/token/', {
            'username': 'teacher1',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, 401)
