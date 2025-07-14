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
from django.utils.timezone import make_aware
from .permission import IsTeacher
from io import TextIOWrapper
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.http import HttpResponse
import csv
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Student, Teacher
from .serializers import PasswordResetRequestSerializer
from .utils import send_password_reset_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .models import Exam, Question, ExamAssignment, StudentExamAttempt, StudentAnswer
from .serializers import ExamSerializer, ExamAssignmentSerializer, StudentExamAttemptSerializer
from rest_framework import generics, permissions, status
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils import timezone

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
                return [IsAuthenticated()]  
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

class ImportStudentsCSV(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')

        if not csv_file.name.endswith('.csv'):
            return Response({"error": "Invalid file format"}, status=status.HTTP_400_BAD_REQUEST)

        data_set = TextIOWrapper(csv_file.file, encoding='utf-8')
        csv_reader = csv.DictReader(data_set)
        created = 0

        for row in csv_reader:
            if not User.objects.filter(username=row['username']).exists():
                user = User.objects.create_user(
                    username=row['username'],
                    password=row['password'],
                    email=row['email']
                )
                teacher = Teacher.objects.get(id=row['assigned_teacher_id']) if 'assigned_teacher_id' in row else None
                Student.objects.create(
                    user=user,
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    email=row['email'],
                    phone_number=row['phone_number'],
                    roll_number=row['roll_number'],
                    student_class=row['student_class'],
                    date_of_birth=row['date_of_birth'],
                    admission_date=row['admission_date'],
                    status=row['status'],
                    assigned_teacher=teacher
                )
                created += 1

        return Response({"message": f"{created} students imported successfully"}, status=status.HTTP_201_CREATED)

class PasswordResetRequestView(APIView):
    permission_classes = []  # No auth needed

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            send_password_reset_email(user, request)
            return Response({"message": "Password reset link sent to your email."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(APIView):
    permission_classes = []  
    
    def post(self, request, uidb64, token):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({'error': 'Both password fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid link or user.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password has been reset successfully!'}, status=status.HTTP_200_OK)

class ExamCreateView(generics.CreateAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class AssignExamView(generics.CreateAPIView):
    serializer_class = ExamAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        exam_id = request.data.get('exam')
        student_ids = request.data.get('students')  
        
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)

        for sid in student_ids:
            try:
                student = User.objects.get(id=sid)
                ExamAssignment.objects.get_or_create(exam=exam, student=student)
            except User.DoesNotExist:
                return Response({'error': f'Student with id {sid} not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'message': 'Exam assigned successfully'}, status=status.HTTP_201_CREATED)

class ExamAssignView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        exam_id = request.data.get('exam_id')
        student_id = request.data.get('student_id')

        try:
            exam = Exam.objects.get(id=exam_id)
            student = Student.objects.get(id=student_id)

            if student.assigned_teacher.user.id == exam.teacher.id:
                ExamAssignment.objects.create(exam=exam, student=student)
                return Response({"detail": "Exam assigned successfully."})
            else:
                return Response({"detail": "You can only assign your exam to your students."}, status=400)

        except Exam.DoesNotExist:
            return Response({"detail": "Exam not found."}, status=404)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=404)

class AttemptExamView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, exam_id):
        user = request.user
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({'error': 'Exam not found'}, status=404)

        if not ExamAssignment.objects.filter(exam=exam, student=user).exists():
            return Response({'error': 'Not assigned to this exam'}, status=403)

        try:
            attempt = StudentExamAttempt.objects.get(student=user, exam=exam)
            if attempt.score is not None:
                return Response({'message': 'Exam already attempted and submitted'}, status=403)


            time_elapsed = timezone.now() - attempt.started_at
            if time_elapsed > timedelta(seconds=exam.duration):
                return Response({'error': 'Exam time expired'}, status=403)

            return Response({'message': 'Exam already started'}, status=200)

        except StudentExamAttempt.DoesNotExist:
    
            StudentExamAttempt.objects.create(student=user, exam=exam, started_at=timezone.now())
            return Response({'message': 'Exam begun'}, status=200)

    def post(self, request, exam_id):
        user = request.user
        score = request.data.get('score')

        if score is None:
            return Response({'error': 'Score not provided'}, status=400)

        try:
            exam = Exam.objects.get(id=exam_id)
            attempt = StudentExamAttempt.objects.get(student=user, exam=exam)
        except (Exam.DoesNotExist, StudentExamAttempt.DoesNotExist):
            return Response({'error': 'Invalid exam or attempt'}, status=404)

      
        if attempt.score is not None:
            return Response({'message': 'Exam already submitted'}, status=403)

        
        time_elapsed = timezone.now() - attempt.started_at
        if time_elapsed > timedelta(seconds=exam.duration):
            return Response({'error': 'Exam time expired'}, status=403)

        
        attempt.score = score
        attempt.save()

        return Response({'message': 'Exam submitted successfully'}, status=201)

class AssignedExamsListView(generics.ListAPIView):
    serializer_class = ExamAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        now = timezone.now()

        assignments = ExamAssignment.objects.filter(student=user)

        valid_assignments = []
        for assignment in assignments:
            exam = assignment.exam
            if StudentExamAttempt.objects.filter(exam=exam, student=user).exists():
                continue
            exam_start_time = assignment.assigned_at
            exam_end_time = exam_start_time + timezone.timedelta(minutes=exam.duration)
            if now > exam_end_time:
                continue

            valid_assignments.append(assignment.id)

        return ExamAssignment.objects.filter(id__in=valid_assignments)
