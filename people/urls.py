from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImportStudentsCSV, PasswordResetConfirmView, PasswordResetRequestView,
    TeacherViewSet, StudentViewSet,
    CustomTokenObtainPairView, ExportTeachersCSV, ExportStudentsCSV,
    ImportTeachersCSV, ExamCreateView, AssignExamView, ExamAssignView, AttemptExamView,
    AssignedExamsListView,ExamDetailView
)
from rest_framework_simplejwt.views import TokenRefreshView
from .views import TeacherCreatedExamsView

router = DefaultRouter()
router.register('teachers', TeacherViewSet)
router.register('students', StudentViewSet, basename='students')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('export/students/', ExportStudentsCSV.as_view(), name='export_students_csv'),
    path('export/teachers/', ExportTeachersCSV.as_view(), name='export_teachers_csv'),
    path('import/students/', ImportStudentsCSV.as_view(), name='import_students_csv'),
    path('import/teachers/', ImportTeachersCSV.as_view(), name='import_teachers_csv'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('exams/create/', ExamCreateView.as_view(), name='exam-create'),
    path('exams/assign/', AssignExamView.as_view(), name='exam-assign'),
    path('exams/assigned/', AssignedExamsListView.as_view(), name='exam-assigned'),
    path('exams/<int:exam_id>/attempt/', AttemptExamView.as_view(), name='exam-attempt'),
    path('exams/created-by-me/', TeacherCreatedExamsView.as_view(), name='teacher-created-exams'),
    path('exams/<int:pk>/', ExamDetailView.as_view(), name='exam-detail'),
]