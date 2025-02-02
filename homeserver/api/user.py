from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import serializers, status
from api.models import User
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from api.auth import JwtAuth


class UserAuthAPI(APIView):
    permission_classes = [AllowAny]
    
    class UserAuthAPIInputSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField()
    
    def post(self, request):
        serializer = self.UserAuthAPIInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.filter(username=data['username']).first()

        if user is None or not user.check_password(data['password']):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        jwt_token = JwtAuth.create_jwt(user)

        return Response({'token': jwt_token}, status=status.HTTP_200_OK)


class UserDetailAPI(APIView):

    class UserDetailAPIOutputSerializer(serializers.Serializer):
        username = serializers.CharField()
        id = serializers.UUIDField()
        email = serializers.EmailField()
        is_staff = serializers.BooleanField(default=False)
        is_active = serializers.BooleanField(default=False)

    
    def get(self, request):

        userSerializer = self.UserDetailAPIOutputSerializer(request.user)
        return Response(userSerializer.data, status=status.HTTP_200_OK)