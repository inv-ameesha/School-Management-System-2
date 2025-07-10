from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from .models import Teacher, Student

# ✅ Custom form for Teacher creation
class TeacherAdminForm(forms.ModelForm):
    username = forms.CharField(label="Username for Login")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = Teacher
        exclude = ['user']  # Hide user field in admin form

    def save(self, commit=True):
        username = self.cleaned_data.pop('username')
        password = self.cleaned_data.pop('password')

        # Avoid duplicate usernames
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("User with this username already exists.")

        user = User.objects.create_user(username=username, password=password)
        self.instance.user = user  # Link to Teacher.user
        return super().save(commit)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    form = TeacherAdminForm
    list_display = ('first_name', 'last_name', 'email', 'subject')

# ✅ Custom form for Student creation
class StudentAdminForm(forms.ModelForm):
    username = forms.CharField(label="Username for Login")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = Student
        exclude = ['user']  # Hide user field in admin form

    def save(self, commit=True):
        username = self.cleaned_data.pop('username')
        password = self.cleaned_data.pop('password')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("User with this username already exists.")

        user = User.objects.create_user(username=username, password=password)
        self.instance.user = user
        return super().save(commit)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ('first_name', 'last_name', 'email', 'student_class')
