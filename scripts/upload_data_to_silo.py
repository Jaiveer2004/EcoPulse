import hashlib
from pathlib import Path

from ecopulse.object_storage import (
    create_s3_client,
    ensure_bucket_exists,
    get_bucket_name,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
            
    return digest.hexdigest()


def get_content_type(path: Path) -> str:
    if path.suffix.lower() == ".jsonl":
        return "application/x-ndjson"
    
    if path.suffix.lower() == ".json":
        return "application/json"
    
    if path.suffix.lower() == ".csv":
            return "text/csv"
        
    return "application/octet-stream"


def upload_file(client, bucket: str, path: Path) -> dict:
    relative_path = path.relative_to(DATA_DIR).as_posix()
    checksum = calculate_sha256(path)
    
    client.upload_file(
        str(path),
        bucket,
        relative_path,
        ExtraArgs={
            "ContentType": get_content_type(path),
            "Metadata": {
                "sha256": checksum,
                "ecopulse-source-path": relative_path,
            },
        },
    )
    
    # Verify the uploaded object's metadata and size.
    response = client.head_object(
        Bucket=bucket,
        Key=relative_path,
    )
    
    if response["ContentLength"] != path.stat().st_size:
        raise RuntimeError(
            f"Size verification failed: {relative_path}"
        )
        
    stored_checksum = response.get("Metadata", {}).get("sha256")
    
    if stored_checksum != checksum:
        raise RuntimeError(
            f"Checksum metadata verification failed: {relative_path}"
        )

    return {
        "key": relative_path,
        "size": path.stat().st_size,
        "sha256": checksum,
    }


def main() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    client = create_s3_client()
    bucket = get_bucket_name()
    
    ensure_bucket_exists(client, bucket)
    
    files = sorted(
        path for path in DATA_DIR.rglob("*")
        if path.is_file()
    )
    
    if not files:
        print("No files found inside the data directory.")
        return
    
    print(f"\nUploading {len(files)} files to Silo...")
    print(f"Bucket: {bucket}\n")

    total_bytes = 0


    for path in files:
        result = upload_file(client, bucket, path)
        
        total_bytes += result["size"]
        
        print(
            f"UPLOADED | {result['key']} "
            f"| {result['size']} bytes"
        )
        
        print("\nUpload completed successfully.")
    print(f"Files uploaded: {len(files)}")
    print(f"Total bytes: {total_bytes}")


if __name__ == "__main__":
    main()
