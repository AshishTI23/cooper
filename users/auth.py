from django.core.cache import cache
from users.models import User
from django.contrib.auth import authenticate, login
from base.authentication import JWTAuthentication


class OTPAuthentication:
    def __init__(self, request, phone, otp):
        self.phone = phone
        self.otp = otp
        self.request = request

    def login(self):
        self.user = User.objects.get(phone=self.phone)
        if self.user.is_active:
            login(self.request, self.user)
            token = JWTAuthentication.create_jwt(self.user)
            return token

    def logout(self):
        pass

    def validate_otp(self):
        if cache.get(self.phone) == self.otp:
            return True
        return False
