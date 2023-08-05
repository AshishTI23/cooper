from django.contrib import admin
from django.urls import path
from users.views import GenerateOTPAPIView

urlpatterns = [
    path("generate_otp/", GenerateOTPAPIView.as_view()),
]
