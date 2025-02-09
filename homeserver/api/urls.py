from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api.user import UserAuthAPI, UserDetailAPI
from api.file import UserUploadFileAPI, UserFileAPI

urlpatterns = [
    path("auth/", UserAuthAPI.as_view(), name="user authentication"),
    path("refresh/", TokenRefreshView.as_view(), name="user token refresh"),
    # user apis
    path("user/", UserDetailAPI.as_view(), name="user details"),
    # upload files
    path("file/upload/", UserUploadFileAPI.as_view(), name="user file upload"),
    # files
    path("file/", UserFileAPI.as_view(), name="user file"),
]
