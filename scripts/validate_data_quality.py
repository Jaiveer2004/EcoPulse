import json
from pathlib import Path
from datetime import datetime, UTC

from pydantic import ValidationError

from ecopulse.models.air_quality import AirQualityRecord
from ecopulse.models.weather import WeatherRecord


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict[int, dict | None, str | None]]:
    """Read JSONL records while preserving malformed-line information."""
    records = []

    with Path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                records.append((line_number, json.load(line), None))
            except json.JSONDecodeError as exc:
                records.append((line_number, None, str(exc)))

    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def validate_file(
    input_path: Path, output_path: Path, model_class, source_name: str
) -> dict:
    input_records = read_jsonl(input_path)

    valid_records = []
    rejected_records = []

    for line_number, record, parse_error in input_records:
        if parse_error is not None:
            rejected_records.append(
                {
                    "line_number": line_number,
                    "errors": [
                        {
                            "type": "json_decode_errors",
                            "message": parse_error,
                        }
                    ],
                }
            )
            continue

        try:
            validated = model_class.model_validate(record)

            valid_records.append(validated.model_dump(mode="json"))

        except ValidationError as exc:
            rejected_records.append(
                {
                    "line_number": line_number,
                    "record": record,
                    "errors": json.loads(exc.json(include_url=False)),
                }
            )

        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        output_path.mkdir(parents=True, exist_ok=True)

        file_prefix = f"{input_path.stem}_{timestamp}"

        write_jsonl(output_path / f"validated_{file_prefix}.jsonl", valid_records)

        write_jsonl(output_path / f"rejected{file_prefix}.jsonl", rejected_records)
        
        total = len(input_records)
        valid_count = len(valid_records)
        rejected_count = len(rejected_records)
        
        return {
            "source": source_name,
            "input_file": str(input_path.relative_to(PROJECT_ROOT)),
            "total_records": total,
            "valid_records": valid_count,
            "rejected_records": rejected_count,
            "quality_rate_percent": (
                round(valid_count / total * 100, 2) if total else 0
            ),
        }


def main() -> None:
    air_files = sorted(
        (PROJECT_ROOT / "data/processed/openaq").glob(
            "measurements_*.jsonl"
        )
    )
    
    weather_files = sorted(
            (PROJECT_ROOT / "data/processed/openmeteo").glob(
                "weather_*.jsonl"
            )
        )
    
    results = []
    
    for path in air_files:
        results.append(
            validate_file(
                path,
                PROJECT_ROOT / "data/validated/openaq",
                AirQualityRecord,
                "openaq"
            )
        )
        
    for path in weather_files:
            results.append(
                validate_file(
                    path,
                    PROJECT_ROOT / "data/validated/openmeteo",
                    WeatherRecord,
                    "openmeteo"
                )
            )
            
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    
    report = {
        "pipeline": "EcoPulse Data Quality Validation",
        "validated_at": datetime.now(UTC).isoformat(),
        "files_processed": len(results),
        "results": results,
    }
    
    report_dir = PROJECT_ROOT / "data/quality_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = report_dir / f"quality_{timestamp}.json"
    
    report_path.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )
    
    print("\nEcoPulse Data Quality Report")
    print("=" * 35)
    
    if not results:
        print("No normalized input files found.")
        
    for result in results:
        print(f"\nSource: {result['source']}")
        print(f"Input: {result['input_file']}")
        print(f"Total: {result['total_records']}")
        print(f"Valid: {result['valid_records']}")
        print(f"Rejected: {result['rejected_records']}")
        print(f"Quality rate: {result['quality_rate_percent']}%")

    print(f"\nFull report: {report_path}")
    
    
if __name__ == "__main__":
    main()