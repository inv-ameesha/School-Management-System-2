from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django import forms
from people.admin import TeacherAdminForm, StudentAdminForm, TeacherAdmin, StudentAdmin
from people.models import Teacher, Student


class AdminTestCase(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.teacher_admin = TeacherAdmin(Teacher, self.admin_site)
        self.student_admin = StudentAdmin(Student, self.admin_site)
        

        teacher_user = User.objects.create_user(username='teacher', password='pass123')
        self.teacher = Teacher.objects.create(
            user=teacher_user,
            first_name='Teacher',
            last_name='One',
            email='teacher@example.com',
            phone=1234567890,
            subject='Math',
            e_id='T001',
            doj='2023-01-01',
            status='Active'
        )

    def test_teacher_admin_form_valid(self):
        form_data = {
            'username': 'newteacher',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': 1234567890,
            'subject': 'Math',
            'e_id': 'T123',
            'doj': '2023-01-01',
            'status': 'Active'
        }
        form = TeacherAdminForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        
       
        teacher = form.save()
        self.assertEqual(teacher.first_name, 'John')
        self.assertEqual(teacher.last_name, 'Doe')
        self.assertEqual(teacher.user.username, 'newteacher')
        self.assertTrue(teacher.user.check_password('password123'))

    def test_teacher_admin_form_duplicate_username(self):
       
        User.objects.create_user(username='existinguser', password='pass123')
        
        form_data = {
            'username': 'existinguser',  
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': 1234567890,
            'subject': 'Math',
            'e_id': 'T123',
            'doj': '2023-01-01',
            'status': 'Active'
        }
        form = TeacherAdminForm(data=form_data)
        
        form.is_valid()
        with self.assertRaises(forms.ValidationError):
            form.save()

    def test_teacher_admin_form_save_without_commit(self):
        form_data = {
            'username': 'newteacher',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': 1234567890,
            'subject': 'Math',
            'e_id': 'T123',
            'doj': '2023-01-01',
            'status': 'Active'
        }
        form = TeacherAdminForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        
        teacher = form.save(commit=False)
        self.assertEqual(teacher.first_name, 'John')
       
        self.assertTrue(User.objects.filter(username='newteacher').exists())

    def test_student_admin_form_valid(self):
        
        teacher = self.teacher
        
        form_data = {
            'username': 'newstudent',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone_number': '9876543210',
            'roll_number': 'R123',
            'student_class': '10A',
            'date_of_birth': '2008-01-01',
            'admission_date': '2023-06-01',
            'status': 'Active',
            'assigned_teacher': teacher.id
        }
        form = StudentAdminForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        
        
        student = form.save()
        self.assertEqual(student.first_name, 'Jane')
        self.assertEqual(student.last_name, 'Smith')
        self.assertEqual(student.user.username, 'newstudent')
        self.assertTrue(student.user.check_password('password123'))
        self.assertEqual(student.assigned_teacher, teacher)

    def test_student_admin_form_duplicate_username(self):
        
        User.objects.create_user(username='existinguser', password='pass123')
        
        form_data = {
            'username': 'existinguser',  
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone_number': '9876543210',
            'roll_number': 'R123',
            'student_class': '10A',
            'date_of_birth': '2008-01-01',
            'admission_date': '2023-06-01',
            'status': 'Active',
            'assigned_teacher': self.teacher.id
        }
        form = StudentAdminForm(data=form_data)
        
        form.is_valid()
        with self.assertRaises(forms.ValidationError):
            form.save()

    def test_student_admin_form_save_without_commit(self):
        
        teacher = self.teacher
        
        form_data = {
            'username': 'newstudent',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone_number': '9876543210',
            'roll_number': 'R123',
            'student_class': '10A',
            'date_of_birth': '2008-01-01',
            'admission_date': '2023-06-01',
            'status': 'Active',
            'assigned_teacher': teacher.id
        }
        form = StudentAdminForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        
        student = form.save(commit=False)
        self.assertEqual(student.first_name, 'Jane')
        
        self.assertTrue(User.objects.filter(username='newstudent').exists())

    def test_teacher_admin_list_display(self):
        
        self.assertEqual(self.teacher_admin.list_display, ('first_name', 'last_name', 'email', 'subject'))

    def test_student_admin_list_display(self):
        
        self.assertEqual(self.student_admin.list_display, ('first_name', 'last_name', 'email', 'student_class'))

    def test_teacher_admin_form_meta(self):
        
        form = TeacherAdminForm()
        self.assertNotIn('user', form.fields)

    def test_student_admin_form_meta(self):
        
        form = StudentAdminForm()
        self.assertNotIn('user', form.fields)

    def test_teacher_admin_form_validation_error_handling(self):
        
        form_data = {
            'username': 'newteacher',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': 1234567890,
            'subject': 'Math',
            'e_id': 'T123',
            'doj': '2023-01-01',
            'status': 'Active'
        }
        
        
        User.objects.create_user(username='newteacher', password='pass123')
        
        form = TeacherAdminForm(data=form_data)
        
        form.is_valid()
        with self.assertRaises(forms.ValidationError):
            form.save()

    def test_student_admin_form_validation_error_handling(self):
        
        form_data = {
            'username': 'newstudent',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone_number': '9876543210',
            'roll_number': 'R123',
            'student_class': '10A',
            'date_of_birth': '2008-01-01',
            'admission_date': '2023-06-01',
            'status': 'Active',
            'assigned_teacher': self.teacher.id
        }
        
        
        User.objects.create_user(username='newstudent', password='pass123')
        
        form = StudentAdminForm(data=form_data)
        
        form.is_valid()
        with self.assertRaises(forms.ValidationError):
            form.save() 