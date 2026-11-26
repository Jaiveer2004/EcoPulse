
# EcoPulse Object Storage Architecture

## Storage technology

PGSTY Silo provides S3-compatible object storage.

## Connection

- Endpoint: http://127.0.0.1:9000
- Console: http://127.0.0.1:9001
- Python SDK: Boto3
- Addressing: Path-style S3

## Bucket

ecopulse-data

## Object prefixes

| Prefix | Purpose |
|---|---|
| raw/ | Original API responses |
| processed/ | Normalized records |
| validated/ | Pydantic-approved records |
| synthetic/ | Synthetic sensor events |
| quality_reports/ | Data quality reports |

## Upload process

1. Discover local data files.
2. Calculate SHA-256 checksums.
3. Upload files using Boto3.
4. Store checksum and source-path metadata.
5. Verify uploaded object size and metadata.

## Important decisions

- Local files are retained after uploading.
- Raw source files are not modified.
- Synthetic and real data remain separated.
- Object keys preserve the local data directory structure.
- Timestamped filenames reduce accidental key collisions.

## Current limitations

- Application currently uses local Silo credentials.
- Object versioning and lifecycle policies are not configured.
- Full download checksum verification is still pending.
- No automated scheduled upload process exists yet.

These are future hardening tasks.
