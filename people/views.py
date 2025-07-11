from rest_framework import viewsets, generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from .models import Teacher, Student
from .serializers import (
    TeacherSerializer,
    StudentSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)
from .permission import IsTeacher
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.http import HttpResponse
import csv

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsTeacher()]
        return [IsAdminUser()]

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsTeacher])
    def me(self, request):
        teacher = Teacher.objects.filter(user=request.user).first()
        if not teacher:
            return Response({'detail': 'No teacher profile found for this user.'}, status=404)
        serializer = self.get_serializer(teacher)
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get_permissions(self):
        user = self.request.user
        if self.action == 'me':
            return [IsAuthenticated()]
        if self.request.method == 'GET':
            if user.is_superuser:
                return [IsAdminUser()]
            elif Student.objects.filter(user=user).exists():
                return [IsAuthenticated()]  # Allow student to access own details
            else:
                return [IsTeacher()]
        if self.request.method == 'POST':
            return [IsAdminUser()] if user.is_superuser else [IsTeacher()]
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAdminUser()] if user.is_superuser else [IsTeacher()]
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Student.objects.all()
        elif Teacher.objects.filter(user=user).exists():
            teacher = Teacher.objects.get(user=user)
            return Student.objects.filter(assigned_teacher=teacher)
        elif Student.objects.filter(user=user).exists():
            student = Student.objects.get(user=user)
            return Student.objects.filter(id=student.id)
        else:
            return Student.objects.none()
        return Student.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser:
            serializer.save()
        else:
            teacher = Teacher.objects.filter(user=user).first()
            serializer.save(assigned_teacher=teacher)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.is_superuser:
            return super().retrieve(request, *args, **kwargs)

        if Teacher.objects.filter(user=user).exists():
            teacher = Teacher.objects.get(user=user)
            if instance.assigned_teacher == teacher:
                return super().retrieve(request, *args, **kwargs)
            return Response({"detail": "You do not have permission to access this student."}, status=403)

        if Student.objects.filter(user=user).exists():
            student = Student.objects.get(user=user)
            if instance.id == student.id:
                return super().retrieve(request, *args, **kwargs)
            return Response({"detail": "You do not have permission to access this student."}, status=403)

        return Response({"detail": "Permission denied."}, status=403)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.is_superuser:
            return super().update(request, *args, **kwargs)

        if Teacher.objects.filter(user=user).exists():
            teacher = Teacher.objects.get(user=user)
            if instance.assigned_teacher == teacher:
                return super().update(request, *args, **kwargs)
            return Response({"detail": "You do not have permission to edit this student."}, status=403)

        return Response({"detail": "Permission denied."}, status=403)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"detail": "Only admin can delete students."}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        student = Student.objects.filter(user=request.user).first()
        if not student:
            return Response({'detail': 'Student profile not found'}, status=404)
        serializer = self.get_serializer(student)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-teacher/(?P<teacher_id>[^/.]+)')
    def by_teacher(self, request, teacher_id=None):
        if not request.user.is_superuser:
            return Response({'detail': 'Permission denied'}, status=403)
        students = Student.objects.filter(assigned_teacher_id=teacher_id)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAdminUser]


class ExportStudentsCSV(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        students = Student.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Roll No', 'Class'])

        for s in students:
            writer.writerow([s.first_name, s.last_name, s.email, s.phone_number, s.roll_number, s.student_class])
        return response


class ExportTeachersCSV(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        teachers = Teacher.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="teachers.csv"'
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Subject'])

        for t in teachers:
            writer.writerow([t.first_name, t.last_name, t.email, t.phone, t.subject])
        return response