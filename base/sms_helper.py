from twilio.rest import Client

import environ

env = environ.Env()


class TwilioSMS:
    def __init__(self, body, to_phone):
        self.body = body
        self.to_phone = to_phone
        self.client = Client(env("TWILIO_SID"), env("TWILIO_AUTH_TOKEN"))

    def send_sms(self):
        return self.client.messages.create(
            from_=env("TWILIO_PHONE_NUMBER"), body=self.body, to=self.to_phone
        )
