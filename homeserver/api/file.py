from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import serializers, status
from rest_framework.response import Response
from api.models import UserFile

class UserUploadFileAPI(APIView):

    parser_classes = [MultiPartParser, JSONParser]

    class UserUploadFileInputSerializer(serializers.Serializer):
        file = serializers.FileField()

    class UserUploadFileOutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        file = serializers.FileField()
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()


    def post(self, request):
        serializers = self.UserUploadFileInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)

        user = request.user
        data = serializers.validated_data

        user_file = UserFile.objects.create(user=user, file=data['file'])

        output_serializer = self.UserUploadFileOutputSerializer(user_file)


        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


        