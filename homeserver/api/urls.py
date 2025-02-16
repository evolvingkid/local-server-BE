from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api.user import UserAuthAPI, UserDetailAPI, UserUIFlagsAPI
from api.file import (
    UserUploadFileAPI,
    UserFileAPI,
    GenerateUploadTokenAPI,
    AddUpdatedTokenFileAPI,
)

urlpatterns = [
    path("auth/", UserAuthAPI.as_view(), name="user authentication"),
    path("refresh/", TokenRefreshView.as_view(), name="user token refresh"),
    path("ui-flag/", UserUIFlagsAPI.as_view(), name="user details"),
    # user apis
    path("user/", UserDetailAPI.as_view(), name="user details"),
    # upload files
    path("file/upload/", UserUploadFileAPI.as_view(), name="user file upload"),
    path(
        "file/upload_token/",
        GenerateUploadTokenAPI.as_view(),
        name="upload token generation",
    ),
    path(
        "file/add-user-files/",
        AddUpdatedTokenFileAPI.as_view(),
        name="user upload file upload",
    ),
    # files
    path("file/", UserFileAPI.as_view(), name="user file"),
]
