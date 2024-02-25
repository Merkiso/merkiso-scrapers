from botocore.exceptions import ClientError
from botocore.config import Config
from io import BytesIO
import boto3

from .settings import (
    MINIO_ACCESS_KEY,
    MINIO_BUCKET_NAME,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    MINIO_USES_SSL,
)


class MinioFilesManager:
    def __init__(self):
        try:
            self.bucket_name = MINIO_BUCKET_NAME
            self.s3 = boto3.client(
                "s3",
                endpoint_url=MINIO_ENDPOINT,
                aws_access_key_id=MINIO_ACCESS_KEY,
                aws_secret_access_key=MINIO_SECRET_KEY,
                use_ssl=MINIO_USES_SSL,
                config=Config(
                    s3={
                        "addressing_style": "path",
                    },
                    signature_version="s3v4",
                ),
            )
        except Exception as e:
            print(f"Error connecting to minio: {e}")
    def upload_public_file(self, filename: str, data: BytesIO):
        unique_name = f"{filename}.json"

        key = f"jsons/{unique_name}"
        
        data.seek(0)

        try:
            self.s3.put_object(
                Body=data.read(),
                Bucket=self.bucket_name,
                Key=key,
                ContentType='application/json',
            )
        except ClientError as e:
            print(f"Se produjo un error al cargar {filename}: {e}")
            return None
        return {
            'key': key,
            'original_name': filename,
            'url': f'{MINIO_ENDPOINT.replace("http://minio", "http://localhost")}/{MINIO_BUCKET_NAME}/{key}',  # noqa
        }

    def get_public_file(self, filename: str):
       
        try:
            response = self.s3.get_object(
                Bucket=self.bucket_name,
                Key=f'jsons/{filename}.json',
            )
            return response['Body'].read()
        except Exception as e:
            return None
    

minio_files_manager = MinioFilesManager()
