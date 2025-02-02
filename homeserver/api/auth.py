from rest_framework import authentication
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed, ParseError
from api.models import User
from datetime import datetime, timedelta


class JwtAuth(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Get the token from the request
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return None

        jwt_token = JwtAuth.get_the_token_from_header(token=token)

        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature')
        except:
            raise ParseError()
        
        username = payload.get('user_identifier')
        if username is None:
            raise AuthenticationFailed('User identifier not found in JWT')
        
        user = User.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        
        return user, payload
    
    def authenticate_header(self, request):
        return 'Bearer'
    
    @classmethod
    def create_jwt(cls, user):
        # Create the JWT payload
        payload = {
            'user_identifier': user.username,
            'exp': int((datetime.now() + timedelta(hours=settings.JWT_CONF['TOKEN_LIFETIME_HOURS'])).timestamp()),
            # set the expiration time for 5 hour from now
            'iat': datetime.now().timestamp(),
            'username': user.username,
        }

        # Encode the JWT with your secret key
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return jwt_token


    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace('Bearer', '').replace(' ', '')  # clean the token
        return token