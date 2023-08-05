from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK


class SuccessResponse(Response):
    def __init__(self, data=None, success_message=None, *args, **kwargs):
        data = {
            "data": data if data else {},
            "success": True,
            "success_message": success_message,
        }
        super().__init__(data, status=HTTP_200_OK, *args, **kwargs)


class ErrorResponse(Response):
    def __init__(self, error=None, *args, **kwargs):
        data = {
            "error_message": error
            if error
            else "Error not provided but I assure you something went wrong!",
            "success": False,
        }
        super().__init__(data, status=HTTP_400_BAD_REQUEST, *args, **kwargs)
