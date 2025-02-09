from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import serializers, status
from api.models import User
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from api.cache_keys import Cache_keys
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

        user = User.objects.filter(username=data["username"]).first()

        if user is None or not user.check_password(data["password"]):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        jwt_token = JwtAuth.create_jwt(user)

        return Response({"token": jwt_token}, status=status.HTTP_200_OK)


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


class UserUIFlagBaseUtils:
    routes = [
        {"page": "file", "permission": "all"},
        {"page": "setting", "permission": "all"},
        {"page": "user_creation", "permission": "admin"},
        {"page": "server_setting", "permission": "admin"},
    ]

    def check_user_permission(self, user):

        permission_settings = []

        for route in self.routes:
            if route.get("permission") == "admin" and user.is_staff:
                permission_settings.append(route.get("page"))

            if route.get("permission") == "all":
                permission_settings.append(route.get("page"))

        return permission_settings

    def ui_flag(self, user):

        permission = self.check_user_permission(user=user)

        return {"permission": permission}


class UserUIFlagsAPI(APIView):

    def get(self, request):
        user = request.user

        cache_ui_flag = cache.get(f"{Cache_keys.ui_flag}-{user.id}")

        ui_flag = cache_ui_flag

        if cache_ui_flag is None:
            ui_flag = UserUIFlagBaseUtils().ui_flag(user=user)

            cache.set(f"{Cache_keys.ui_flag}-{user.id}", ui_flag, timeout=43200)

        return Response({"data": ui_flag}, status.HTTP_200_OK)
