import uuid

from ecopulse.object_storage import (
    create_s3_client,
    ensure_bucket_exists,
    get_bucket_name,
)


def main() -> None:
    client = create_s3_client()
    bucket = get_bucket_name()

    print("Connecting to EcoPulse Silo...")

    ensure_bucket_exists(client, bucket)

    # Verify bucket access.
    response = client.list_buckets()

    bucket_names = [item["Name"] for item in response.get("Buckets", [])]

    if bucket not in bucket_names:
        raise RuntimeError("Bucket was not found after creation")

    print(f"Bucket access verified: {bucket}")

    # Upload a temporary test object.
    key = f"system-tests/connection-tests-{uuid.uuid4()}.txt"
    original_content = b"EcoPulse Silo connectivity test"

    client.put_object(
        Bucket=bucket, Key=key, Body=original_content, ContentType="text/plain"
    )

    print("Test object uploaded.")

    response = client.get_object(
        Bucket=bucket,
        Key=key,
    )

    downloadable_content = response["Body"].read()

    if downloadable_content != original_content:
        raise RuntimeError("Downloaded object does not match uploaded data")

    print("Upload/download verification passed.")

    client.delete_object(
        Bucket=bucket,
        Key=key,
    )

    print("Temporary test object deleted.")
    print("\nSilo connection test completed successfully!")


if __name__ == "__main__":
    main()
