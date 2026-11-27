import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx

from ecopulse.ingestion.openaq import create_client
from ecopulse.logging_config import configure_logging, get_logger
from ecopulse.source_config import get_source_config

configure_logging()
logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "openaq"

PAGE_SIZE = 1000
LOOKBACK_DAYS = 7

TARGET_SENSORS = [
    {"sensor_id": 15243, "parameter": "pm25", "unit": "µg/m³"},
    {"sensor_id": 12235142, "parameter": "pm25", "unit": "µg/m³"},
    {"sensor_id": 15260, "parameter": "pm10", "unit": "µg/m³"},
    {"sensor_id": 12235141, "parameter": "pm10", "unit": "µg/m³"},
]


class OpenAQMeasurementError(Exception):
    """Raised when OpenAQ measurement ingestion fails."""


def get_date_window() -> tuple[str, str]:
    now = datetime.now(UTC)
    start = now - timedelta(days=LOOKBACK_DAYS)

    return (
        start.isoformat(timespec="seconds").replace("+00:00", "Z"),
        now.isoformat(timespec="seconds").replace("+00:00", "Z"),
    )


def fetch_sensor_measurement(
    sensor_id: int,
    date_from: str,
    date_to: str,
) -> list[dict]:
    records = []

    params = {
        "datetime_from": date_from,
        "datetime_to": date_to,
        "limit": PAGE_SIZE,
        "page": 1,
    }

    try:
        with create_client() as client:
            while True:
                response = client.get(
                    f"/sensors/{sensor_id}/measurements", params=params
                )

                response.raise_for_status()

                payload = response.json()

                if not isinstance(payload, dict):
                    raise OpenAQMeasurementError("Invalid measurement response")

                results = payload.get("results")

                if not isinstance(results, list):
                    raise OpenAQMeasurementError("Missing measurement results")

                records.extend(results)

                logger.info(
                    "Sensor %s | Page %s | Retrieved %s records",
                    sensor_id,
                    params["page"],
                    len(results),
                )

                if len(results) < PAGE_SIZE:
                    break

                params["page"] += 1
    except httpx.HTTPStatusError as exc:
        logger.exception(
            "OpenAQ HTTP error for sensor %s",
            sensor_id,
        )

        raise OpenAQMeasurementError(
            f"OpenAQ returned HTTP {exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        logger.exception(
            "OpenAQ connection error for sensor %s",
            sensor_id,
        )
        raise OpenAQMeasurementError(
            f"Connection failed for sensor: {sensor_id}"
        ) from exc

    except ValueError as exc:
        logger.exception(
            "Invalid JSON for sensor %s",
            sensor_id,
        )
        raise OpenAQMeasurementError("OpenAQ returned invalid JSON") from exc

    return records


def save_sensor_measurements(
    sensor: dict, records: list[dict], date_from: str, date_to: str
) -> Path:
    config = get_source_config()
    ingested_at = datetime.now(UTC)

    envelope = {
        "source_type": "real",
        "source_name": "openaq",
        "data_kind": "original_sensor_measurements",
        "region": config.region,
        "country": config.country,
        "location_name": "Model Town, Patiala - PPCB",
        "sensor_id": sensor["sensor_id"],
        "parameter": sensor["parameter"],
        "unit": sensor["unit"],
        "requested_window": {
            "datetime_from": date_from,
            "datetime_to": date_to,
        },
        "ingested_at": ingested_at.isoformat(),
        "record_count": len(records),
        "raw_payload": records,
    }

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    filename = (
        f"sensor_{sensor['sensor_id']}_{ingested_at.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    )

    output_path = RAW_DATA_DIR / filename
    temp_path = output_path.with_suffix(".tmp")

    try:
        temp_path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
        temp_path.replace(output_path)
    except OSError:
        temp_path.unlink(missing_ok=True)
        logger.exception(
            "Unable to save measurements for sensor %s",
            sensor["sensor_id"],
        )
        raise

    return output_path


def run_measurement_ingestion() -> list[Path]:
    logger.info("Starting OpenAQ measurement ingestion")

    date_from, date_to = get_date_window()
    output_files = []

    for sensor in TARGET_SENSORS:
        sensor_id = sensor["sensor_id"]

        logger.info(
            "Fetching %s measurements for sensor %s",
            sensor["parameter"],
            sensor_id,
        )

        records = fetch_sensor_measurement(sensor_id, date_from, date_to)

        output_path = save_sensor_measurements(sensor, records, date_from, date_to)

        output_files.append(output_path)

        logger.info(
            "Sensor %s ingestion completed: %s records",
            sensor_id,
            len(records),
        )

    logger.info(
        "OpenAQ measurement ingestion completed. Files: %s",
        len(output_files),
    )

    return output_files
