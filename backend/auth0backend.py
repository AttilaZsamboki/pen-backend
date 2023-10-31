import requests
from jose import jwt
from rest_framework import authentication, exceptions


class Auth0JSONWebTokenAuthentication(authentication.BaseAuthentication):
    www_authenticate_realm = "api"

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != b"bearer":
            return None

        if len(auth) == 1:
            msg = "Invalid Authorization header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = "Invalid Authorization header. Credentials string should not contain spaces."
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = "Invalid token. Token string should not contain invalid characters."
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        # Fetch the public key from Auth0
        url = "https://dev-1aujvjsopd1xpcyu.us.auth0.com/.well-known/jwks.json"
        response = requests.get(url)
        jwks = response.json()
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == jwt.get_unverified_header(token)["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }

        # Decode the token and verify its validity
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience="https://pen.dataupload.xyz/felmeresek/",
                issuer="https://dev-1aujvjsopd1xpcyu.us.auth0.com/",
            )
        except jwt.JWTError:
            msg = "Invalid token."
            raise exceptions.AuthenticationFailed(msg)

        return (payload, token)
