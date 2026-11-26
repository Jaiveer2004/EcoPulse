
from ecopulse.object_storage import (
    create_s3_client,
    get_bucket_name,
)


def main() -> None:
    client = create_s3_client()
    bucket = get_bucket_name()

    paginator = client.get_paginator("list_objects_v2")

    total_objects = 0

    print(f"\nObjects inside bucket: {bucket}\n")

    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            print(
                f"{obj['Key']} | "
                f"{obj['Size']} bytes"
            )
            total_objects += 1

    print(f"\nTotal objects: {total_objects}")


if __name__ == "__main__":
    main()
