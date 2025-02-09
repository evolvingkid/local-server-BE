from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import serializers, status
from rest_framework.response import Response
from api.models import UserFile, S3AccessClient
from django.conf import settings
from datetime import datetime
from api.serializers import CustomPagination


class UserFileAPI(APIView, CustomPagination):

    class UserUploadFileOutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        file = serializers.CharField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()
        file_url = serializers.CharField()

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
