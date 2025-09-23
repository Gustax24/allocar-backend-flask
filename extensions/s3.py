import boto3
from botocore.client import Config

def get_s3_client(app):
    session = boto3.session.Session()
    return session.client(
        "s3",
        endpoint_url=app.config.get("S3_ENDPOINT_URL"),
        aws_access_key_id=app.config.get("S3_ACCESS_KEY"),
        aws_secret_access_key=app.config.get("S3_SECRET_KEY"),
        region_name=app.config.get("S3_REGION"),
        config=Config(signature_version="s3v4"),
        use_ssl=app.config.get("S3_SECURE", False),
    )
