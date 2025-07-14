from django.test import TestCase
from django.contrib.auth.models import User
from people.models import (
    Teacher, Student, Exam, Question, ExamAssignment,
    StudentExamAttempt, StudentAnswer
)
from datetime import date, timedelta
from django.utils import timezone


class ModelTests(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='teacheruser')
        self.student_user = User.objects.create_user(username='studentuser')
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone=1234567890,
            subject="Math",
            e_id="T123",
            doj="2023-01-01",
            status="Active"
        )

        self.student = Student.objects.create(
            user=self.student_user,
            first_name="Amy",
            last_name="Antony",
            email="amy@example.com",
            phone_number="9999999999",
            roll_number="R001",
            student_class="10A",
            date_of_birth="2010-01-01",
            admission_date="2023-06-01",
            status="Active",
            assigned_teacher=self.teacher
        )

    def test_teacher_str(self):
        self.assertEqual(str(self.teacher), "John Doe")

    def test_student_str(self):
        self.assertEqual(str(self.student), "Amy Antony")

    def test_exam_creation(self):
        exam = Exam.objects.create(
            title="Math Final",
            subject="Math",
            date="2024-05-01",
            duration=60,
            teacher=self.teacher_user
        )
        self.assertEqual(exam.title, "Math Final")

    def test_question_creation(self):
        exam = Exam.objects.create(
            title="Physics Final",
            subject="Physics",
            date="2024-05-02",
            duration=90,
            teacher=self.teacher_user
        )
        question = Question.objects.create(
            exam=exam,
            text="What is gravity?",
            option_a="Force",
            option_b="Mass",
            option_c="Velocity",
            option_d="Energy",
            correct_option="a"
        )
        self.assertEqual(question.text, "What is gravity?")

    def test_exam_assignment_str(self):
        exam = Exam.objects.create(
            title="Science Test",
            subject="Science",
            date="2024-07-01",
            duration=45,
            teacher=self.teacher_user
        )
        assignment = ExamAssignment.objects.create(
            exam=exam,
            student=self.student_user
        )
        self.assertEqual(str(assignment), "studentuser -> Science Test")

    def test_student_exam_attempt_str(self):
        exam = Exam.objects.create(
            title="Biology Quiz",
            subject="Biology",
            date="2024-08-01",
            duration=30,
            teacher=self.teacher_user
        )
        attempt = StudentExamAttempt.objects.create(
            exam=exam,
            student=self.student_user,
            score=90,
            submitted=True
        )
        self.assertEqual(str(attempt), "studentuser - Biology Quiz")

    def test_student_answer_creation(self):
        exam = Exam.objects.create(
            title="Chemistry Midterm",
            subject="Chemistry",
            date="2024-06-01",
            duration=50,
            teacher=self.teacher_user
        )
        question = Question.objects.create(
            exam=exam,
            text="H2O is?",
            option_a="Salt",
            option_b="Acid",
            option_c="Water",
            option_d="Base",
            correct_option="c"
        )
        attempt = StudentExamAttempt.objects.create(
            exam=exam,
            student=self.student_user,
            score=None,
            submitted=False
        )
        answer = StudentAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_option="C"
        )
        self.assertEqual(answer.selected_option, "C")
