from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImportStudentsCSV, PasswordResetConfirmView, PasswordResetRequestView,
    TeacherViewSet, StudentViewSet,
    CustomTokenObtainPairView, ExportTeachersCSV, ExportStudentsCSV,
    ImportTeachersCSV, ExamCreateView, AssignExamView, ExamAssignView, AttemptExamView,
    TransactionLogView,SimulateRazorpayPaymentView,FineCalculationView
    AssignedExamsListView,ExamDetailView,FeeAllocationView,InitiatePaymentView,PaymentOptionsView,VerifyRazorpayPaymentView
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
    path('fee-allocation/', FeeAllocationView.as_view(), name='fee-allocation'),
    path('pay/options/', PaymentOptionsView.as_view(), name='payment-options'),
    path('pay/initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('pay/verify/', VerifyRazorpayPaymentView.as_view(), name='verify-payment'),
    path("transactions/logs/", TransactionLogView.as_view(), name="transaction-logs"),
    # path("transactions/pay/<int:student_fee_id>/", PaymentProcessView.as_view(), name="payment-process"),
    path("simulate/", SimulateRazorpayPaymentView.as_view(), name="simulate-payment"),
    if settings.DEBUG:  
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
     path("calculate-fine/", FineCalculationView.as_view(), name="calculate-fine"),
]