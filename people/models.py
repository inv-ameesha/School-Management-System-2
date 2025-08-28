from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

# class SchoolClass(models.Model):
#     grade = models.IntegerField()  
#     academic_year = models.CharField(max_length=20)  
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('grade', 'academic_year')  
#         db_table = "school_classes" 

#     def __str__(self):
#         return f"Class {self.grade} - {self.academic_year}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    phone=models.IntegerField(default=0)
    subject=models.CharField(max_length=50)
    e_id=models.CharField(max_length=20,unique=True)
    doj=models.DateField()
    status=models.CharField(max_length=10,choices=[('Active','Active'),('Inactive','Inactive')])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    roll_number = models.CharField(max_length=20, unique=True)
    grade = models.IntegerField(null=True, blank=True)  
    academic_year = models.CharField(max_length=20,null=True, blank=True)  
    date_of_birth = models.DateField()
    admission_date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    assigned_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Exam(models.Model):
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    date = models.DateField()
    duration = models.IntegerField(default=30)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

class Question(models.Model):
    exam = models.ForeignKey(Exam, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    
    CORRECT_OPTIONS = [
        ('a', 'Option A'),
        ('b', 'Option B'),
        ('c', 'Option C'),
        ('d', 'Option D'),
    ]
    correct_option = models.CharField(max_length=1, choices=CORRECT_OPTIONS)

class ExamAssignment(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.student.username} -> {self.exam.title}"


class StudentExamAttempt(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(null=True, blank=True) 
    submitted = models.BooleanField(default=False)

    def is_time_over(self):
        return self.start_time + timedelta(minutes=self.exam.duration_minutes) < timezone.now()

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(StudentExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])

class FeeStructure(models.Model):
    grade = models.IntegerField(null=True) 
    academic_year = models.CharField(max_length=20)  
    base_fee = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    fine_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('grade', 'academic_year')

    def __str__(self):
        return f"Class {self.grade} - {self.academic_year}"

class StudentFee(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)  
    fee_structure = models.ForeignKey('FeeStructure', on_delete=models.CASCADE)  
    total_amount = models.DecimalField(max_digits=10, decimal_places=2) 
    due_date = models.DateField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student} - {self.fee_structure.academic_year} - {self.status}"        

class Payment(models.Model):
    student_fee = models.ForeignKey('StudentFee', on_delete=models.CASCADE)
    
    GATEWAY_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('offline', 'Offline'),
    ]
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # from gateway
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    payment_date = models.DateTimeField(default=timezone.now)
    remarks = models.TextField(null=True, blank=True)
   
    def __str__(self):
        return f"Payment {self.id} - {self.status} - {self.amount}"

class TransactionLog(models.Model):
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE, null=True, blank=True)
    
    log_message = models.TextField()
    
    LOG_TYPES = [
        ('info', 'Info'),
        ('error', 'Error'),
        ('warning', 'Warning'),
    ]
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, default='info')
    
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Log {self.id} - {self.log_type}"

class Receipt(models.Model):
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=50, unique=True)  
    student = models.ForeignKey('Student', on_delete=models.CASCADE)  
    fee_structure = models.ForeignKey('FeeStructure', on_delete=models.CASCADE)  
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)  
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    receipt_file = models.CharField(max_length=255, null=True, blank=True)  
    issued_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.student}"

class Fine(models.Model):
    student_fee = models.ForeignKey('StudentFee', on_delete=models.CASCADE)
    
    days_overdue = models.IntegerField()
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)
    calculated_on = models.DateField()

    def __str__(self):
        return f"Fine {self.fine_amount} for {self.student_fee}"

class Notification(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    
    NOTIFICATION_TYPES = [
        ('due_reminder', 'Due Reminder'),
        ('overdue', 'Overdue Reminder'),
        ('payment_success', 'Payment Success'),
    ]
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    message = models.TextField()
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Notification {self.type} to {self.student}"