from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Extract the JWT from the Authorization header
        jwt_token = request.META.get("HTTP_AUTHORIZATION")
        if jwt_token is None:
            return None

        jwt_token = JWTAuthentication.clean_jwt_token(jwt_token)

        # Decode the JWT and verify its signature
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed("Invalid signature")
        except:
            raise ParseError()

        # Get the user from the database
        user_id = payload.get("user_id")
        phone = payload.get("phone")
        if user_id is None:
            raise AuthenticationFailed("User identifier not found in JWT")

        user = User.objects.filter(phone=phone).first()
        if user is None:
            user = User.objects.filter(pk=user_id).first()
            if user is None:
                raise AuthenticationFailed("User not found")

        # Return the user and JWT token
        return user, payload

    def authenticate_header(self, request):
        return "Bearer"

    @classmethod
    def create_jwt(cls, user):
        # Create the JWT payload
        payload = {
            "user_id": user.id,
            "exp": int((datetime.now() + timedelta(hours=10)).timestamp()),
            "iat": datetime.now().timestamp(),
            "phone_number": user.phone,
        }

        # Encode the JWT with your secret key
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return jwt_token

    @classmethod
    def clean_jwt_token(cls, token):
        token = token.replace("Bearer", "").replace(" ", "")  # clean the token
        return token
