from rest_framework import viewsets, generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from .models import Teacher, Student ,Payment, Exam , Question, ExamAssignment, StudentExamAttempt, StudentAnswer,FeeStructure,StudentFee,TransactionLog,Receipt,Fine
from django.db import transaction
import os
from reportlab.pdfgen import canvas
import hmac, hashlib
from .serializers import (
    TeacherSerializer,
    StudentSerializer,
    CustomTokenObtainPairSerializer,ExamSerializer,
    ExamAssignmentSerializer,StudentExamAttemptSerializer,
    FeeAllocationSerializer,InitiatePaymentSerializer,SimulateRazorpayPaymentSerializer,
    TransactionLogSerializer,FineRequestSerializer
)
import razorpay
import pkg_resources
from django.conf import settings
from rest_framework.views import APIView
from django.utils.timezone import make_aware
from .permission import IsTeacher,IsStudent
from io import TextIOWrapper
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.http import HttpResponse
import csv
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from .models import Student, Teacher
from .serializers import PasswordResetRequestSerializer
from .utils import send_password_reset_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework import generics, permissions, status
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.permissions import AllowAny
from rest_framework.generics import RetrieveAPIView
from datetime import datetime
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
#viewset : allows multiple views within a single class
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()#get the teacher data
    serializer_class = TeacherSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsTeacher()]#if url=me only teacher could access
        return [IsAdminUser()]#else admins also could access;IsAdminUser-inbuilt
    #detail=False : action operates on a list of object not on a single object
    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsTeacher])
    def me(self, request):
        teacher = Teacher.objects.filter(user=request.user).first()#gets the teacher object of the loged in teacher
        if not teacher:
            return Response({'detail': 'No teacher profile found for this user.'}, status=404)
        serializer = self.get_serializer(teacher)#serializes the obtained data
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get_permissions(self):#self:instance of that cls for actions like self.request,self.action etc
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
        student = Student.objects.get(pk=kwargs['pk'])
        student.status = 'Inactive'
        email_address = student.email
        tag = str(datetime.now())
        new_email_address = email_address.replace("@", tag + "@")
        student.email=new_email_address
        print(new_email_address)
        student.save()
        return Response({"detail": "deleted."}, status=202)

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


class ExportStudentsCSV(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Filters from query params
        grade = request.GET.get('grade')               
        start_date = request.GET.get('start_date')     
        end_date = request.GET.get('end_date')       
        status = request.GET.get('status') 
        students = Student.objects.all()
        student_fee = StudentFee.objects.all()
        # Filter by grade
        if grade:
            students = students.filter(grade=grade)
        if status == 'overdue':
            students_overdue = student_fee.filter(status='overdue')
            student_ids = students_overdue.values_list('student_id', flat=True)
            students = students.filter(id__in=student_ids).distinct()
        # Filter students who have at least one paid fee
        paid_fees = StudentFee.objects.filter(status='paid')
        # Apply date range filter
        if start_date and end_date : 
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                paid_fees = paid_fees.filter(created_at__gte=start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                paid_fees = paid_fees.filter(created_at__lte=end_date_obj)
            student_ids = paid_fees.values_list('student_id', flat=True)
            students = students.filter(id__in=student_ids).distinct()

        response = HttpResponse(content_type='text/csv')#mentions that it contains csv data
        response['Content-Disposition'] = 'attachment; filename="students.csv"'#force download
        writer = csv.writer(response)

        # CSV header
        writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Roll No', 'Grade'])

        # CSV rows
        for s in students:
            if not s.status == 'Inactive':
                writer.writerow([s.first_name, s.last_name, s.email, s.phone_number, s.roll_number, s.grade])

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
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("file")

        if not csv_file or not csv_file.name.endswith(".csv"):
            return Response(
                {"error": "Invalid file format"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data_set = TextIOWrapper(csv_file.file, encoding="utf-8")#converts the file into a text stream
        csv_reader = csv.DictReader(data_set)#saves the data in dict format like key-value pair

        created, errors = 0, []
        is_admin = request.user.is_staff
        is_teacher = hasattr(request.user, "teacher")

        for i, row in enumerate(csv_reader, start=1):
            try:

                if User.objects.filter(username=row.get("username")).exists():
                    errors.append(f"Row {i}: Username {row['username']} already exists")
                    continue
                if Student.objects.filter(roll_number=row.get("roll_number")).exists():
                    errors.append(f"Row {i}: Roll number {row['roll_number']} already exists")
                    continue
                if Student.objects.filter(email=row.get("email")).exists():
                    errors.append(f"Row {i}: Email {row['email']} already exists")
                    continue

                teacher = None
                if is_admin and row.get("assigned_teacher_id"):
                    try:
                        teacher = Teacher.objects.get(id=row["assigned_teacher_id"])
                    except Teacher.DoesNotExist:
                        errors.append(
                            f"Row {i}: Teacher with ID {row['assigned_teacher_id']} not found"
                        )
                        continue
                # elif is_teacher:
                #     teacher = request.user.teacher

                with transaction.atomic():
                    # Create user
                    # user = User.objects.create_user(
                    #     username=row["username"],
                    #     password=row["password"],
                    #     email=row["email"]
                    # )

                    # Prepare student data
                    student_data = {
                        "username": row.get("username"),
                        "password": row.get("password"),
                        "email": row.get("email"),
                        "first_name": row.get("first_name"),
                        "last_name": row.get("last_name"),
                        "phone_number": row.get("phone_number"),
                        "roll_number": row.get("roll_number"),
                        "grade": row.get("grade") or None,
                        "academic_year": row.get("academic_year") or None,
                        "date_of_birth": row.get("date_of_birth"),
                        "admission_date": row.get("admission_date"),
                        "status": row.get("status"),
                        "assigned_teacher": teacher.id if teacher else None,
                    }
                    serializer = StudentSerializer(data=student_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

                    created += 1 #used down

            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        return Response(
            {
                "message": f"{created} students imported successfully",
                "errors": errors,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST,
        )

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            send_password_reset_email(user, request)
            return Response({"message": "Password reset link sent to your email."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]  # No auth needed
    
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

class TeacherCreatedExamsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        exams = Exam.objects.filter(teacher=request.user)
        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data)

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
        student_ids = request.data.get('students')  # list of Student IDs

        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({'error': 'Exam not found'}, status=404)

        for sid in student_ids:
            student_obj = Student.objects.get(id=sid)
            user_obj = student_obj.user
            ExamAssignment.objects.get_or_create(exam=exam, student=user_obj)  # must use user_obj

        return Response({'message': 'Exam assigned successfully'}, status=201)


# Student lists all exams assigned to them
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

    def post(self, request, exam_id):
        user = request.user
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({'error': 'Exam not found'}, status=404)

        # Check if already attempted
        if StudentExamAttempt.objects.filter(student=user, exam=exam).exists():
            return Response({'message': 'Exam already submitted'}, status=403)

        # Create the attempt
        StudentExamAttempt.objects.create(student=user, exam=exam, started_at=timezone.now())
        return Response({'message': 'Exam submitted successfully'}, status=201)

class AssignedExamsListView(generics.ListAPIView):
    serializer_class = ExamAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            student = Student.objects.get(user=user)
            print(student)
        except Student.DoesNotExist:
            return ExamAssignment.objects.none()
        assignments = ExamAssignment.objects.filter(student=user)  # must use user
        valid_assignments = []
        for assignment in assignments:
            exam = assignment.exam
            # Only include if NOT already attempted
            if StudentExamAttempt.objects.filter(exam=exam, student=user).exists():
                continue
            # Only include if NOT expired
            exam_start_time = assignment.assigned_at
            exam_end_time = exam_start_time + timezone.timedelta(minutes=exam.duration)
            if timezone.now() > exam_end_time:
                continue
            # If not attempted and not expired, include in the list
            valid_assignments.append(assignment.id)
        return ExamAssignment.objects.filter(id__in=valid_assignments)

class ExamDetailView(RetrieveAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

class ImportTeachersCSV(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')

        if not csv_file or not csv_file.name.endswith('.csv'):
            return Response({"error": "Invalid file format"}, status=status.HTTP_400_BAD_REQUEST)

        data_set = TextIOWrapper(csv_file.file, encoding='utf-8')
        csv_reader = csv.DictReader(data_set)
        created = 0

        for row in csv_reader:
            if not User.objects.filter(username=row['username']).exists():
                user = User.objects.create_user(
                    username=row['username'],
                    password=row['password'],
                    email=row['email'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )
                Teacher.objects.create(
                    user=user,
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    email=row['email'],
                    phone=row['phone'],
                    subject=row['subject'],
                    date_of_birth=row.get('date_of_birth', None),
                    hire_date=row.get('hire_date', None),
                    status=row.get('status', 'Active')
                )
                created += 1

        return Response({"message": f"{created} teachers imported successfully"}, status=status.HTTP_201_CREATED)

class FeeAllocationView(generics.CreateAPIView):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeAllocationSerializer
    permission_classes = [permissions.IsAdminUser]


class StudentFeeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = request.user.student 
        if not student:
            return Response({"error": "Student not found"}, status=404)
        grade = student.grade
        academic_year = student.academic_year

        fee_structures = FeeStructure.objects.filter(
            student_class=student.grade,
            academic_year=academic_year
        )
        fees = StudentFee.objects.filter(student=student, fee_structure__in=fee_structures)
        for fee in fees:
            fee.update_status()

        serializer = StudentFeeSerializer(fees, many=True)
        return Response(serializer.data)

class PaymentOptionsView(APIView):
    def get(self, request):
        return Response({"options": ["razorpay", "offline"]})

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated,IsStudent]

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student_fee_id = serializer.validated_data['student_fee_id']
        gateway = serializer.validated_data['gateway']
        with transaction.atomic():#single fetch transaction
                try:
                    student_fee = StudentFee.objects.select_for_update().get(
                        id=student_fee_id, student=request.user.student
                    )#select_for_update() - implements row-level locking in that student_fee row
                except StudentFee.DoesNotExist:
                    return Response(
                        {"error": "Student fee not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                if student_fee.lock == 1:
                    return Response({"error": "Payment is already being processed for this fee."}, status=400)

                student_fee.lock = 1
                student_fee.save()

                if student_fee.status == "paid":
                    student_fee.lock = 0  
                    student_fee.save()
                    return Response({"error": "Fee already paid"}, status=400)

                today = timezone.now().date()
                if today > student_fee.due_date:
                    days_overdue = (today - student_fee.due_date).days
                    fine_amount = days_overdue * student_fee.fee_structure.fine_per_day
                else:
                    days_overdue = 0
                    fine_amount = 0
                try:
                    # Update or create Fine record
                    Fine.objects.update_or_create(
                        student_fee=student_fee,
                        student=student_fee.student,
                        defaults={
                            "days_overdue": days_overdue,
                            "fine_amount": fine_amount,
                            "calculated_on": today,
                        }
                    )
                except Exception as e:
                    return Response(
                        {"error": f"Failed to update fine: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                student_fee.total_amount = student_fee.fee_structure.base_fee + fine_amount
                student_fee.save()

                existing_payment = Payment.objects.filter(
                    student_fee=student_fee,
                    status="initiated"
                ).first()
                if existing_payment:
                    return Response({"error": "Payment already initiated"}, status=400)

                if gateway == "razorpay":
                    try:
                        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                        amount_in_paise = int(student_fee.total_amount * 100)#razorpay expects the smallest currency unit
                        order = client.order.create({
                            "amount": amount_in_paise,
                            "currency": "INR",
                            "receipt": f"{student_fee.id}",
                            "payment_capture": 1#razopay auto capture the payment
                        })
                    except razorpay.errors.BadRequestError as e:
                        return Response(
                            {"error": f"Invalid Razorpay request: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    except razorpay.errors.ServerError as e:
                        return Response(
                            {"error": f"Razorpay server error: {str(e)}"},
                            status=status.HTTP_502_BAD_GATEWAY
                        )
                    except Exception as e:
                        TransactionLog.objects.create(
                            payment=None,
                            log_message=f"Razorpay order creation failed for StudentFee {student_fee.id}: {str(e)}",
                            log_type="error"
                        )
                        return Response({"error": "Failed to create Razorpay order"}, status=500)
                    try:
                        payment = Payment.objects.create(
                            student_fee=student_fee,
                            gateway="razorpay",
                            transaction_id=order['id'],
                            amount=student_fee.total_amount,
                            status="initiated"
                        )
                        TransactionLog.objects.create(
                            payment=payment,
                            log_message=f"Payment initiated via Razorpay, order_id={order['id']}",
                            log_type="info"
                        )
                        return Response({
                            "order_id": order['id'],
                            "amount": student_fee.total_amount,
                            "currency": "INR",
                            "payment_id": payment.id
                        })
                    except Exception as e:
                        return Response(
                            {"error": f"Failed to create Payment record: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

                elif gateway == "offline":
                    try:
                        payment = Payment.objects.create(
                            student_fee=student_fee,
                            gateway="offline",
                            amount=student_fee.total_amount,
                            status="success",
                            remarks="Cash / Offline payment"
                        )
                        student_fee.paid_amount = student_fee.total_amount
                        student_fee.status = "paid"
                        student_fee.save()
                        
                        TransactionLog.objects.create(
                            payment=payment,
                            log_message="Payment marked as offline success",
                            log_type="info"
                        )
                        return Response({"message": "Payment marked as offline success", "payment_id": payment.id})
                    except Exception as e:
                        return Response(
                            {"error": f"Failed to create offline payment: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                else:
                    return Response(
                        {"error": f"Unsupported payment gateway: {gateway}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
        # except StudentFee.DoesNotExist:
        #     return Response({"error": "Student fee not found"}, status=status.HTTP_404_NOT_FOUND)

class VerifyRazorpayPaymentView(APIView):
    permission_classes = [IsAuthenticated,IsStudent]

    def post(self, request):
        data =  request.data
        #extract required fields
        payment_id = data.get('payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        if not all([payment_id, razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response(
                {"error": "Missing required payment fields"},
                status=status.HTTP_400_BAD_REQUEST
            )
        #authenticate with razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            TransactionLog.objects.create(
                payment_id=payment_id,
                log_message="Razorpay signature verification failed",
                log_type="error"
            )
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Unexpected error during signature verification: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        #get payment record
        try:
            payment = Payment.objects.get(id=payment_id, transaction_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"Error fetching payment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        try:
            payment.status = "success"
            payment.transaction_id = razorpay_payment_id
            payment.save()

            # Update StudentFee
            student_fee = payment.student_fee
            student_fee.paid_amount = student_fee.total_amount
            student_fee.status = "paid"
            student_fee.lock = 0
            student_fee.save()

            TransactionLog.objects.create(
                payment=payment,
                log_message=f"Payment verified successfully. Razorpay Payment ID: {razorpay_payment_id}",
                log_type="success"
            )
        except Exception as e:
            return Response(
                {"error": f"Error updating payment/student fee: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            # Generate receipt PDF
            receipt_folder = os.path.join(settings.MEDIA_ROOT, 'receipts')
            os.makedirs(receipt_folder, exist_ok=True)

            filename = f"RCPT_{payment.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            file_path = os.path.join(receipt_folder, filename)
            receipt_path = f"receipts/{filename}"  # relative path for model

            c = canvas.Canvas(file_path)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(200, 800, "Fee Payment Receipt")
            c.setFont("Helvetica", 12)
            c.drawString(50, 750, f"Student Name: {student_fee.student.first_name} {student_fee.student.last_name}")
            c.drawString(50, 730, f"Roll Number: {student_fee.student.roll_number}")
            c.drawString(50, 710, f"Class/Grade: {student_fee.student.grade}")
            c.drawString(50, 690, f"Academic Year: {student_fee.fee_structure.academic_year}")
            c.drawString(50, 670, f"Total Fee Paid: ₹{student_fee.total_amount}")
            c.drawString(50, 650, f"Payment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(50, 630, f"Payment Method: Razorpay")
            c.drawString(50, 610, f"Transaction ID: {razorpay_payment_id}")
            c.showPage()
            c.save()

        except Exception as e:
            return Response(
                {"error": f"Error generating receipt PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        try:
            # Save receipt entry
            receipt = Receipt.objects.create(
                payment=payment,
                receipt_number=f"RCPT{payment.id}",
                student=student_fee.student,
                fee_structure=student_fee.fee_structure,
                amount_paid=payment.amount,
                fine_amount=0,
                total_amount=payment.amount,
                receipt_file=receipt_path,
                issued_date=timezone.now()
            )

            # Build URL for API response
            receipt_url = request.build_absolute_uri(settings.MEDIA_URL + receipt.receipt_file)

            return Response({"message": "Payment successful", "receipt_url": receipt_url})

        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found"}, status=404)

class TransactionLogView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        #get logs from the latest to oldest
        logs = TransactionLog.objects.all().order_by('-created_at')
        serializer = TransactionLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class PaymentProcessView(APIView):
#     def post(self, request, student_fee_id):
#         try:
#             with transaction.atomic():
#                 # lock student fee row
#                 student_fee = StudentFee.objects.select_for_update().get(id=student_fee_id)

#                 if student_fee.status == "paid":
#                     TransactionLog.objects.create(
#                         payment=None,
#                         log_message=f"Payment already completed for StudentFee {student_fee_id}",
#                         log_type="warning"
#                     )
#                     return Response({"error": "Already paid"}, status=status.HTTP_400_BAD_REQUEST)

#                 # create a payment record
#                 payment = Payment.objects.create(
#                     student_fee=student_fee,
#                     gateway=request.data.get("gateway", "offline"),
#                     transaction_id=request.data.get("transaction_id", None),
#                     amount=student_fee.total_amount,
#                     status="initiated"
#                 )

#                 # Mark fee as paid
#                 student_fee.status = "paid"
#                 student_fee.save()

#                 # update payment status
#                 payment.status = "success"
#                 payment.save()

#                 # log success
#                 # TransactionLog.objects.create(
#                 #     payment=payment,
#                 #     log_message=f"Payment {payment.id} processed successfully for StudentFee {student_fee.id}",
#                 #     log_type="info"
#                 # )

#                 return Response({"message": "Payment success"}, status=status.HTTP_200_OK)

#         except StudentFee.DoesNotExist:
#             TransactionLog.objects.create(
#                 payment=None,
#                 log_message=f"StudentFee {student_fee_id} not found",
#                 log_type="error"
#             )
#             return Response({"error": "Student fee not found"}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             TransactionLog.objects.create(
#                 payment=None,
#                 log_message=f"Payment failed for StudentFee {student_fee_id} - {str(e)}",
#                 log_type="error"
#             )
#             return Response({"error": "Payment failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SimulateRazorpayPaymentView(APIView):
    permission_classes = [IsAuthenticated,IsStudent]
    def post(self, request):
        try:
            serializer = SimulateRazorpayPaymentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {"error": f"Invalid input: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        payment_id = serializer.validated_data['payment_id']
        razorpay_order_id = serializer.validated_data['razorpay_order_id']

        try:
            payment = Payment.objects.get(id=payment_id, transaction_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"Error fetching payment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        try:
            # fake payment id from Razorpay
            razorpay_payment_id = f"pay_{payment_id}XYZ"
        except Exception as e:
            return Response(
                {"error": f"Failed to generate payment_id: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        try:
            # generate signature
            msg = f"{razorpay_order_id}|{razorpay_payment_id}"
            generated_signature = hmac.new(
                bytes(settings.RAZORPAY_KEY_SECRET, "utf-8"),
                bytes(msg, "utf-8"),
                hashlib.sha256
            ).hexdigest()
        except Exception as e:
            return Response(
                {"error": f"Failed to generate signature: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        TransactionLog.objects.create(
            payment=payment,
            log_message=f"Simulated Razorpay payment generated. razorpay_payment_id={razorpay_payment_id}",
            log_type="info"
        )
        try:
            # return payload same as Razorpay would give
            return Response({
                "payment_id": payment_id,
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": generated_signature
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to build response: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# class FineCalculationView(APIView):
#     def post(self, request):
#         # Validate input
#         serializer = FineRequestSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         student_fee_id = serializer.validated_data["student_fee_id"]

#         # Fetch StudentFee
#         try:
#             student_fee = StudentFee.objects.get(id=student_fee_id)
#         except StudentFee.DoesNotExist:
#             return Response({"error": "StudentFee not found"}, status=status.HTTP_404_NOT_FOUND)

#         today = date.today()

#         # Case 1: Already paid and on/before due date → No fine
#         if student_fee.status == "paid" and student_fee.paid_on and student_fee.paid_on <= student_fee.due_date:
#             return Response({"message": "No fine applicable. Payment already on time."}, status=status.HTTP_200_OK)

#         # Case 2: Overdue
#         overdue_days = (today - student_fee.due_date).days
#         if overdue_days > 0:
#             fine_amount = Decimal(overdue_days) * student_fee.fine_per_day  

#             fine, created = Fine.objects.get_or_create(
#                 student_fee=student_fee,
#                 calculated_on=today,
#                 defaults={
#                     "days_overdue": overdue_days,
#                     "fine_amount": fine_amount
#                 }
#             )

#             fine_data = FineSerializer(fine).data
#             fine_data["status"] = "fine_created" if created else "fine_already_exists"

#             return Response(fine_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

#         return Response({"message": "No fine applicable yet."}, status=status.HTTP_200_OK)

class StudentFeeAlertView(APIView):
    permission_classes = [IsAuthenticated,IsStudent]

    def get(self, request):
        #get the corresponsing student record
        try:
            student = Student.objects.get(user=request.user)  
        except Student.DoesNotExist:
            return Response({"message": "Student record not found"}, status=404)
        #get the corresponsing student fee record
        try:
            student_fee = StudentFee.objects.get(student=student)
        except StudentFee.DoesNotExist:
            return Response({"message": "No fee record found"}, status=404)

        if student_fee.status.lower() == "paid":
            return Response({"message": "Fee already paid. No alert required."}, status=200)

        fine = Fine.objects.filter(student_fee=student_fee).order_by('-calculated_on').first()

        return Response({
            "due_date": student_fee.due_date,
            "base_fee": student_fee.fee_structure.base_fee,
            "fine_amount": fine.fine_amount if fine else 0,
            "days_overdue": fine.days_overdue if fine else 0,
            "total_amount": student_fee.total_amount
        })

class ReceiptUploadView(APIView):
    permission_classes = [IsAuthenticated,IsStudent]
    parser_classes = [MultiPartParser]

    def post(self, request):
        student = request.user.student  

        # Find student's fee record which is already uploaded
        student_fee = StudentFee.objects.filter(student=student, status="uploaded").first()
        if student_fee:
            return Response(
                {"error": "Receipt uploaded"},
                status=status.HTTP_404_NOT_FOUND
            )
        # Find student's fee record which has not paid yet
        student_fee = StudentFee.objects.filter(student=student, status="paid").first()
        if not student_fee:
            return Response(
                {"error": "No paid fee found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Ensure only PDF upload
        uploaded_file = request.FILES.get("receipt")#key in postman
        if not uploaded_file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        if not uploaded_file.name.lower().endswith(".pdf") or uploaded_file.content_type != "application/pdf":
            return Response({"error": "Only PDF receipts are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        # Update status to uploaded (don’t save file)
        student_fee.status = "uploaded"
        student_fee.save()

        return Response({
            "message": "Receipt uploaded successfully",
            "status": student_fee.status
        }, status=status.HTTP_200_OK)
