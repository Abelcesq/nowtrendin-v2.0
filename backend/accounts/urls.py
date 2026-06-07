from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('google/', views.GoogleAuthView.as_view()),
    path('me/', views.MeView.as_view()),
    path('change-password/', views.ChangePasswordView.as_view()),
    path('forgot-password/', views.ForgotPasswordView.as_view()),
    path('reset-password/', views.ResetPasswordView.as_view()),
    path('phone/send-code/', views.SendPhoneCodeView.as_view()),
    path('phone/verify/', views.VerifyPhoneView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
]
