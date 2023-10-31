import jwt
import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Get the token from the request headers or any other location
        token = self.get_token_from_header(request)

        if token is None:
            return None

        try:
            # Decode the token
            decoded_token = jwt.decode(
                token,
                "your_secret_key",
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
        # Implement your logic to retrieve the user information associated with the token
        # This could involve querying your database or any other data source
        # Return a user-like object or user information

        url = "https://login.auth0.com/api/v2/roles/:id/users"

        payload = {}
        headers = {"Accept": "application/json"}

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

        return None
