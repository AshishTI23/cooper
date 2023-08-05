from django.core.cache import cache
from users.models import User
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class OTPAuthentication:
    def __init__(self, request, phone, otp):
        self.phone = phone
        self.otp = otp
        self.request = request

    def login(self):
        self.user = User.objects.get(phone=self.phone)
        if self.user.is_active:
            login(self.request, self.user)
            payload = jwt_payload_handler(self.user)
            token = jwt_encode_handler(payload)
            return token

    def logout(self):
        pass

    def validate_otp(self):
        if cache.get(self.phone) == self.otp:
            return True
        return False
