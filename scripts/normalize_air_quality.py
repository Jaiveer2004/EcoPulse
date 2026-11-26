import json
from datetime import UTC, datetime
from pathlib import Path

from ecopulse.ingestion.openaq_normalizer import normalize_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "openaq"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "openaq"


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    raw_files = sorted(RAW_DIR.glob("sensor_*.json"))

    if not raw_files:
        raise FileNotFoundError(f"No sensor measurement files found in {RAW_DIR}")

    all_normalized = []
    all_rejected = []

    for file_path in raw_files:
        normalized, rejected = normalize_file(file_path)

        all_normalized.extend(normalized)
        all_rejected.extend(rejected)

        print(
            f"{file_path.name}: {len(normalized)} normalized, {len(rejected)} rejected"
        )

    normalized_path = OUTPUT_DIR / f"measurements_{timestamp}.jsonl"
    rejected_path = OUTPUT_DIR / f"rejected_{timestamp}.jsonl"

    write_jsonl(normalized_path, all_normalized)
    write_jsonl(rejected_path, all_rejected)

    print("\nNormalization completed!")
    print(f"Total normalized: {len(all_normalized)}")
    print(f"Total rejected: {len(all_rejected)}")
    print(f"Normalized output: {normalized_path}")
    print(f"Rejected output: {rejected_path}")


if __name__ == "__main__":
    main()
