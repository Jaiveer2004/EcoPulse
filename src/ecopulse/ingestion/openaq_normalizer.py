import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SENSOR_METADATA = {
    15243: {"parameter": "pm25", "unit": "µg/m³"},
    12235142: {"parameter": "pm25", "unit": "µg/m³"},
    15260: {"parameter": "pm10", "unit": "µg/m³"},
    12235141: {"parameter": "pm10", "unit": "µg/m³"},
}


def extract_sensor_id(file_path: Path, envelope: dict) -> int:
    """Get sensor ID from metadata or the raw filename."""

    metadata = envelope.get("metadata", {})
    sensor_id = metadata.get("sensor_id") or envelope.get("sensor_id")

    if sensor_id is None:
        match = re.search(r"sensor_(\d+)", file_path.name)
        if match:
            sensor_id = match.group(1)

    if sensor_id is None:
        raise ValueError(f"Cannot identify sensor ID: {file_path.name}")

    return int(sensor_id)


def extract_timestamp(record: dict) -> str:
    """Extract the UTC timestamp from an OpenAQ measurement."""

    datetime_data = record.get("datetime")
    if datetime_data is None:
        datetime_data = record.get("period", {}).get("datetimeFrom")

    if isinstance(datetime_data, dict):
        timestamp = datetime_data.get("utc")
    elif isinstance(datetime_data, str):
        timestamp = datetime_data
    else:
        timestamp = None

    if not timestamp:
        raise ValueError("Measurement has no UTC timestamp")

    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)

    return parsed.astimezone(UTC).isoformat()


def normalized_record(
    record: dict[str, Any],
    sensor_id: int,
    envelope: dict[str, Any],
) -> dict[str, Any]:
    """Convert one OpenAQ measurement into EcoPulse's normalized schema."""

    sensor = SENSOR_METADATA.get(sensor_id)

    if sensor is None:
        raise ValueError(f"Unknown sensor ID: {sensor_id}")

    value = record.get("value")

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Measurement value must be numeric")

    if not isinstance(value, (int, float)) or not float("-inf") < float(value) < float(
        "inf"
    ):
        raise ValueError("Measurement value must be finite")

    coordinates = record.get("coordinates") or {}

    metadata = envelope.get("metadata", {})
    source_metadata = envelope.get("source_metadata", {})

    return {
        "location_id": (
            source_metadata.get("location_id")
            or metadata.get("location_id")
            or envelope.get("location_id")
        ),
        "sensor_id": sensor_id,
        "parameter": sensor["parameter"],
        "value": float(value),
        "unit": sensor["unit"],
        "observed_at": extract_timestamp(record),
        "latitude": coordinates.get("latitude"),
        "longitude": coordinates.get("longitude"),
        "source_type": envelope.get("source_type", "real"),
        "source_name": envelope.get("source_name", "openaq"),
        "ingested_at": envelope.get("ingested_at"),
        "source_record_id": record.get("id"),
    }

def normalize_file(file_path: Path) -> tuple[list[dict], list[dict]]:
    """Normalize one raw sensor file and collect invalid records separately."""
    
    envelope = json.loads(file_path.read_text(encoding="utf-8"))
    sensor_id = extract_sensor_id(file_path, envelope)
    
    payload = envelope.get("raw_payload", [])
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        records = payload.get("records", [])
    else:
        raise ValueError(f"Expected a results list in {file_path.name}")
    
    if not isinstance(records, list):
        raise ValueError(f"Expected a results list in {file_path.name}")
    
    normalized = []
    rejected = []
    
    for index, record in enumerate(records):
        try:
            normalized.append(
                normalized_record(record, sensor_id, envelope)
            )
        except (ValueError, TypeError, AttributeError) as exc:
            rejected.append({
                "source_file": file_path.name,
                "record_index": index,
                "reason": str(exc),
                "raw_record": record,
            })
            
    return normalized, rejected