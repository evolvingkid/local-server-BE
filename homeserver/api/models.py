import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
import boto3
from django.conf import settings


class S3AccessClient:
    _instance = None
    client = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(S3AccessClient, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def __init__(self, value=None):
        if not hasattr(self, "value"):
            self.value = value

    def init_client(self):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT
        )


S3AccessClient().init_client()


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)


class UserFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.CharField(max_length=124)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_removed = models.BooleanField(default=False)

    @property
    def file_url(self):

        signed_url = S3AccessClient().client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": self.file},
            ExpiresIn=43200,
        )
        return signed_url
