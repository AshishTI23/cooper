from django.contrib import admin
from django.urls import path
from users.views import GenerateOTPAPIView, LoginAPIView

urlpatterns = [
    path("generate_otp/", GenerateOTPAPIView.as_view()),
    path("login/", LoginAPIView.as_view()),
]
