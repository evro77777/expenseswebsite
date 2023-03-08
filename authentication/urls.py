from .views import *
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('validate-username/', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email/', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
    path('activate/<uid64>/<token>/', VerificationView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('request-password/', RequestPasswordResetEmail.as_view(), name='request-password'),
    path('set_password/<uid64>/<token>', VerificationResetPassword.as_view(), name='set_password')

]
