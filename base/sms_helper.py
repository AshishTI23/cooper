from twilio.rest import Client
import random
from django.core.cache import cache


import environ

env = environ.Env()


class TwilioSMS(object):
    def __init__(self, body, to_phone):
        self.body = body
        self.to_phone = to_phone
        self.client = Client(env("TWILIO_SID"), env("TWILIO_AUTH_TOKEN"))

    def send(self):
        return self.client.messages.create(
            from_=env("TWILIO_PHONE_NUMBER"), body=self.body, to=self.to_phone
        )


class OTP(object):
    def __init__(self, phone):
        self.phone = phone

    def generate(self):
        otp = random.randint(1000, 9999)
        cache.set(self.phone, otp, timeout=1000)
        return otp


def get_sms_body(sms_type, otp=None):
    match sms_type:
        case "otp":
            return f"OTP to login in cooper system is: {otp} Do not share with anyone"
