from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from base.sms_helper import OTP, TwilioSMS, get_sms_body
from base.constants import COUNTRY_CODE
from base.http import SuccessResponse, ErrorResponse
from users.serializers import GenerateOTPSerializer

# Create your views here.
class GenerateOTPAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GenerateOTPSerializer(data=request.data)
        if serializer.is_valid():
            otp = OTP(request.data.get("phone")).generate()
            try:
                TwilioSMS(
                    get_sms_body("otp", otp),
                    COUNTRY_CODE.get(request.data.get("country"))
                    + request.data.get("phone"),
                ).send()
            except:
                return ErrorResponse("Failed to send OTP, Looks like invalid phone")
            return SuccessResponse(
                serializer.data, f"An OTP has been set to {request.data.get('phone')}"
            )
        return ErrorResponse(serializer.errors)
