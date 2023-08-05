class FailedToSendMessage(Exception):
    def __init__(self, *args, **kwargs):
        default_message = f"Failed to send sms"
        if not args:
            args = (default_message,)
        # Call super constructor
        super().__init__(*args, **kwargs)
