from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import serializers, status
from rest_framework.response import Response
from api.models import UserFile, S3AccessClient
from django.conf import settings
from datetime import datetime
from api.serializers import CustomPagination
from drf_spectacular.utils import extend_schema


class UserFileAPI(APIView, CustomPagination):

    class UserUploadFileOutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        file = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()
        file_url = serializers.CharField()

    @extend_schema(
        responses={200: UserUploadFileOutputSerializer},
        description="List of file of the user",
    )
    def get(self, request):
        user_files = UserFile.objects.all()
        paginated = self.paginate_queryset(user_files, request, view=self)
        serializer = self.UserUploadFileOutputSerializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)


class UserUploadFileAPI(APIView):

    parser_classes = [MultiPartParser, JSONParser]

    class UserUploadFileInputSerializer(serializers.Serializer):
        file = serializers.FileField()

    class UserUploadFileOutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        file = serializers.URLField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    @extend_schema(
        responses={200: UserUploadFileOutputSerializer},
        description="List of file of the user",
        request=UserUploadFileInputSerializer,
    )
    def post(self, request):
        serializers = self.UserUploadFileInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)

        user = request.user
        data = serializers.validated_data

        file_name = (
            f'user-media/{datetime.now().strftime("%Y%m%d%H%M%S")}-{data["file"].name}'
        )

        client = S3AccessClient().client

        user_media = f"{settings.AWS_STORAGE_BUCKET_NAME}"

        client.upload_fileobj(
            data["file"],
            user_media,
            file_name,
            ExtraArgs={"ContentType": data["file"].content_type},
        )

        client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": file_name},
            ExpiresIn=300,
        )

        user_file = UserFile.objects.create(user=user, file=file_name)

        output_serializer = self.UserUploadFileOutputSerializer(user_file)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class GenerateUploadTokenAPI(APIView):

    class GenerateUploadTokenInputSerializer(serializers.Serializer):
        files = serializers.ListField(
            child=serializers.DictField(
                child=serializers.CharField(),
                required=True,
                validators=[
                    lambda x: all(key in x for key in ["filename", "content_type"]),
                ],
            )
        )

    class GenerateUploadTokenOutputSerializer(serializers.Serializer):
        url = serializers.URLField()
        fields = serializers.DictField()
        filename = serializers.CharField()

    @extend_schema(
        request=GenerateUploadTokenInputSerializer,
        responses={200: GenerateUploadTokenOutputSerializer},
        description="Generate upload token",
    )
    def post(self, request):

        serializer = self.GenerateUploadTokenInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        client = S3AccessClient().client
        token_url = []

        for file_info in data["files"]:
            file_name = f'user-media/{datetime.now().strftime("%Y%m%d%H%M%S")}-{file_info["filename"]}'

            token = client.generate_presigned_post(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_name,
                Fields={
                    "Content-Type": file_info.get(
                        "content_type", "application/octet-stream"
                    )
                },
                Conditions=[
                    ["content-length-range", 0, 10485760],  # Max file size: 10MB
                    ["starts-with", "$Content-Type", ""],
                    ["starts-with", "$key", "user-media/"],
                ],
                ExpiresIn=300,
            )

            token_url.append(
                {"url": token["url"], "fields": token["fields"], "filename": file_name}
            )

        output_serializer = self.GenerateUploadTokenOutputSerializer(
            token_url, many=True
        )

        return Response(output_serializer.data, status=status.HTTP_200_OK)


class AddUpdatedTokenFileAPI(APIView):

    class AddUpdatedTokenFileInputSerializer(serializers.Serializer):
        files = serializers.ListField(child=serializers.CharField())

    class AddUpdatedTokenFileOutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        file = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

    @extend_schema(
        responses={200: AddUpdatedTokenFileOutputSerializer},
        description="List of uploaded file of the user",
        request=AddUpdatedTokenFileInputSerializer,
    )
    def post(self, request):
        serializers = self.AddUpdatedTokenFileInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)

        user = request.user
        data = serializers.validated_data

        user_file = []

        for file in data.get("files"):
            user_file.append(UserFile(file=file, user=user))

        UserFile.objects.bulk_create(user_file)

        return Response({"status": "SUCCESS"}, status=status.HTTP_200_OK)
