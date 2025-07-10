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
            return [IsAdminUser()] if user.is_superuser else [IsTeacher()]
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
        teacher = Teacher.objects.filter(user=user).first()
        return Student.objects.filter(assigned_teacher=teacher)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser:
            serializer.save()
        else:
            teacher = Teacher.objects.filter(user=user).first()
            serializer.save(assigned_teacher=teacher)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user.is_superuser:
            return super().update(request, *args, **kwargs)

        # Only the assigned teacher can update
        teacher = Teacher.objects.filter(user=user).first()
        if instance.assigned_teacher != teacher:
            return Response({"detail": "You do not have permission to edit this student."},
                            status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

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
