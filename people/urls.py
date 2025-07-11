from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherViewSet, StudentViewSet, RegisterView, CustomTokenObtainPairView,ExportTeachersCSV, ExportStudentsCSV
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register('teachers', TeacherViewSet)
router.register('students', StudentViewSet, basename='students')

urlpatterns = [
    path('', include(router.urls)),

    # Auth endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('export/students/', ExportStudentsCSV.as_view(), name='export_students_csv'),
    path('export/teachers/', ExportTeachersCSV.as_view(), name='export_teachers_csv'),
]
