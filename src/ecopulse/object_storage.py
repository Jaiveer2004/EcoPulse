import os
from pathlib import Path

import boto3

from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def create_s3_client():
    endpoint = os.getenv("ECOPULSE_S3_ENDPOINT")
    access_key = os.getenv("MINIO_ROOT_USER")
    secret_key = os.getenv("MINIO_ROOT_PASSWORD")
    region = os.getenv("ECOPULSE_S3_REGION", "us-east-1")

    required = {
        "ECOPULSE_S3_ENDPOINT": endpoint,
        "MINIO_ROOT_USER": access_key,
        "MINIO_ROOT_PASSWORD": secret_key,
    }

    missing = [name for name, value in required.items() if not value]
    
    if missing:
        raise ValueError(
            f"Missing Silo configuration: {', '.join(missing)}"
        )
        
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"}
        ),
    )

def get_bucket_name() -> str:
    bucket = os.getenv("ECOPULSE_S3_BUCKET")
    
    if not bucket:
        raise ValueError("ECOPULSE_S3_BUCKET is not configured")
    
    return bucket


def ensure_bucket_exists(client, bucket_name) -> None:
    try:
        client.head_bucket(Bucket=bucket_name)
        print(f"Bucket already exists: {bucket_name}")
        
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        
        if error_code not in {"404", "NoSuchBucket", "NotFound"}:
            raise
        
        client.create_bucket(Bucket=bucket_name)
        print(f"Created bucket: {bucket_name}")