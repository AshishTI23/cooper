from rest_framework_simplejwt.authentication import JWTAuthentication


class OTPAuthentication:
    def __init__(self, phone, otp):
        self.phone = phone
        self.otp = otp

    def login(self):
        pass

    def logout(self):
        pass

    def validate_otp(self):
        pass
