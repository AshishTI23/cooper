from rest_framework.response import Response


class SuccessResponse(Response):
    def __init__(self, data=None, *args, **kwargs):
        data = {"data": data if data else {}, "success": True}
        super(SuccessResponse, self).__init__(data, *args, **kwargs)


class ErrorResponse(Response):
    def __init__(self, error=None, *args, **kwargs):
        data = {
            "error": error
            if error
            else "Error not provided but I assure you something went wrong!",
            "success": False,
        }
        super(ErrorResponse, self).__init__(data, *args, **kwargs)
