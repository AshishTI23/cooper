from twilio.rest import Client

account_sid = env("TWILIO_SID")
auth_token = env("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

def send_sms_with_twilio(body, to):
    return client.messages.create(from_=env("TWILIO_PHONE_NUMBER"), body=body, to=to)
