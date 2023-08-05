from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from base.sms_helper import OTP, TwilioSMS, get_sms_body
from base.constants import COUNTRY_CODE
from base.exception import FailedToSendMessage
from users.serializers import GenerateOTPSerializer

# Create your views here.
class GenerateOTPAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GenerateOTPSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            otp = OTP(request.data.get("phone")).generate()
            try:
                TwilioSMS(
                    get_sms_body("otp", otp),
                    COUNTRY_CODE.get(request.data.get("country"))
                    + request.data.get("phone"),
                ).send()
            except:
                pass
        return Response("Test API Response")
