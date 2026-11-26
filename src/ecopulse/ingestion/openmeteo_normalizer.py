import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Asia/Kolkata")

WEATHER_VARIABLES = {
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
}


def convert_to_utc(timestamp: str) -> str:
    """Convert an Open-Meteo local timestamp to UTC."""

    parsed = datetime.fromisoformat(timestamp)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=TIMEZONE)

    return parsed.astimezone(UTC).isoformat()


def normalize_weather_file(
    file_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:

    envelope = json.loads(file_path.read_text(encoding="utf-8"))
    payload = envelope.get("raw_payload", {})

    hourly = payload.get("hourly")
    hourly_units = payload.get("hourly_units")

    timestamps = hourly.get("time")

    if not isinstance(timestamps, list):
        raise ValueError(f"Missing hourly timestamps in {file_path.name}")

    normalized = []
    rejected = []

    for variable in WEATHER_VARIABLES:
        values = hourly.get(variable)

        if not isinstance(values, list):
            continue

        if len(values) != len(timestamps):
            raise ValueError(f"Timestamp/value count mismatch for {variable}")

        unit = hourly_units.get(variable)

        if not unit:
            raise ValueError(f"Missing unit for {variable}")

        for index, (timestamp, value) in enumerate(
            zip(timestamps, values, strict=False)
        ):
            try:
                if value is None or isinstance(value, bool):
                    raise ValueError("Weather value is missing or invalid")

                numeric_value = float(value)

                if not math.isfinite(numeric_value):
                    raise ValueError("Weather value must be finite")

                normalized.append(
                    {
                        "parameter": variable,
                        "value": numeric_value,
                        "unit": unit,
                        "valid_at": convert_to_utc(timestamp),
                        "data_kind": "forecast",
                        "time_semantics": "valid_time",
                        "source_type": envelope.get("source_type", "real"),
                        "source_name": envelope.get("source_name", "open_meteo"),
                        "ingested_at": envelope.get("ingested_at"),
                        "latitude": payload.get("latitude"),
                        "longitude": payload.get("longitude"),
                        "region": envelope.get("region", "Patiala"),
                        "country": envelope.get("country", "India"),
                    }
                )

            except (ValueError, TypeError, OverflowError) as exc:
                rejected.append(
                    {
                        "source_file": file_path.name,
                        "parameter": variable,
                        "record_index": index,
                        "reason": str(exc),
                        "raw_timestamp": timestamp,
                        "raw_value": value,
                    }
                )

        return normalized, rejected
