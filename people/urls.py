from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherViewSet, StudentViewSet, RegisterView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register('teachers', TeacherViewSet)
router.register('students', StudentViewSet, basename='students')

urlpatterns = [
    path('', include(router.urls)),

    # 🔐 Custom Role-based JWT Auth
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 🔐 Admin Registration Endpoint
    path('register/', RegisterView.as_view(), name='register'),
]
