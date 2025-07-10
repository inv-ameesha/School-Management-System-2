from rest_framework import viewsets, generics
from rest_framework.permissions import IsAdminUser
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

# 🔐 Custom Token View for Role-based Login
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# 🔹 Admin-only: Manage teachers
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsTeacher()]
        return [IsAdminUser()]

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        teacher = Teacher.objects.filter(user=request.user).first()
        if not teacher:
            return Response({'detail': 'No teacher profile found for this user.'}, status=404)
        serializer = self.get_serializer(teacher)
        return Response(serializer.data)


# 🔹 Admin: All students | Teacher: Own students
class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get_permissions(self):
        user = self.request.user
        if self.request.method == 'GET':
            if user.is_superuser:
                return [IsAdminUser()]
            return [IsTeacher()]
        return [IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Student.objects.all()
        teacher = Teacher.objects.filter(user=user).first()
        return Student.objects.filter(assigned_teacher=teacher)


# 🔹 Admin-only: Register users
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAdminUser]
