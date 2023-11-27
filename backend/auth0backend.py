import jwt
import os

from .models import UserRoles

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SimpleUser:
    def __init__(self, token, is_authenticated):
        self.token = token
        self._is_authenticated = is_authenticated

    @property
    def is_authenticated(self):
        return self._is_authenticated


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Get the token from the request headers or any other location
        if os.environ.get("ENVIRONMENT") == "development":
            token = request.GET.get("token")
        else:
            token = self.get_token_from_header(request)

        if token is None:
            return None

        try:
            # Decode the token
            decoded_token = jwt.decode(
                token,
                os.environ.get("SECRET"),
                algorithms=["HS256"],
                audience="penész-frontend",
            )

            # Validate the claims (e.g., expiration time, audience, issuer)
            if not self.validate_claims(decoded_token):
                raise AuthenticationFailed("Invalid token")

            # Retrieve the user information associated with the token
            user = self.get_user_from_token(decoded_token)

            return (user, token)
        except jwt.ExpiredSignatureError:
            # Token has expired
            print("Token has expired")
        except jwt.InvalidAudienceError:
            # Other JWT-related error
            print("Invalid audience")
        except jwt.InvalidAlgorithmError:
            # Other JWT-related error
            print("Invalid algorithm")
        except jwt.InvalidSignatureError:
            # Other JWT-related error
            print("Invalid signature")
        except jwt.ImmatureSignatureError:
            print("Immature signature")

    def get_token_from_header(self, request):
        # Get the Authorization header from the request
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if auth_header and auth_header.startswith("Bearer "):
            # Extract the token from the Authorization header
            return auth_header.split(" ")[1]

        return None

    def validate_claims(self, decoded_token):
        # Implement your custom claim validation logic here
        # Return True if all claims are valid, False otherwise
        if decoded_token["iss"] != "penészmentesítés":
            return False
        return True

    def get_user_from_token(self, decoded_token):
        return SimpleUser(decoded_token, True)
