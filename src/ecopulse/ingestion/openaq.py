import json
from datetime import datetime, UTC
from pathlib import Path

import httpx

from ecopulse.logging_config import configure_logging, get_logger
from ecopulse.source_config import get_source_config

configure_logging()
logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "openaq"

PAGE_SIZE = 100


class OpenAQIngestionError(Exception):
    """Raised when OpenAQ ingestion fails."""


def create_client() -> httpx.Client:
    config = get_source_config()

    if not config.openaq_api_key:
        raise OpenAQIngestionError("OPENAQ_API_KEY is not configured")

    return httpx.Client(
        base_url=config.openaq_base_url,
        headers={
            "X-API-Key": config.openaq_api_key,
            "Accept": "application/json",
        },
        timeout=30.0,
    )


def get_locations() -> list[dict]:
    config = get_source_config()

    params = {
        "coordinates": (f"{config.latitude},{config.longitude}"),
        "radius": config.search_radius,
        "iso": "IN",
        "limit": PAGE_SIZE,
        "page": 1,
    }

    locations = []

    try:
        with create_client() as client:
            while True:
                response = client.get("/locations", params=params)
                response.raise_for_status()

                payload = response.json()

                if not isinstance(payload, dict):
                    raise OpenAQIngestionError("Invalid locations response")

                results = payload.get("results")

                if not isinstance(results, list):
                    raise OpenAQIngestionError("Missing locations results")

                locations.extend(results)

                logger.info(
                    "Retrieved OpenAQ location page %s: %s records",
                    params["page"],
                    len(results),
                )

                if len(results) < PAGE_SIZE:
                    break

                params["page"] += 1
    except httpx.HTTPStatusError as exc:
        logger.exception("OpenAQ HTTP error")
        raise OpenAQIngestionError(
            f"OpenAQ returned HTTP {exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        logger.exception("Unable to connect to OpenAQ")
        raise OpenAQIngestionError("Unable to connect to OpenAQ") from exc

    except ValueError as exc:
        logger.exception("Invalid JSON response")
        raise OpenAQIngestionError("OpenAQ returned invalid JSON") from exc

    logger.info(
        "Total OpenAQ locations discovered: %s",
        len(locations),
    )

    return locations


def extract_sensor_summary(locations: list[dict]) -> list[dict]:
    sensor_records = []

    for location in locations:
        for sensor in location.get("sensors", []):
            parameter = sensor.get("parameter", {})

            sensor_records.append(
                {
                    "location_id": location.get("id"),
                    "location_name": location.get("name"),
                    "sensor_id": sensor.get("id"),
                    "parameter": parameter.get("name"),
                    "unit": parameter.get("units"),
                    "sensor_last_updated": sensor.get("datetimeLast"),
                }
            )
            
    return sensor_records

def save_raw_locations(locations: list[dict]) -> Path:
    config = get_source_config()
    
    ingested_at = datetime.now(UTC)
    
    envelope = {
        "source_type": "real",
        "source_name": "openaq",
        "data_kind": "station_metadata",
        "region": config.region,
        "country": config.country,
        "requested_coordinates": {
            "latitude": config.latitude,
            "longitude": config.longitude,
        },
        "search_radius_meters": config.search_radius,
        "ingested_at": ingested_at.isoformat(),
        "raw_payload": locations,
    }
    
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    filename = (
        f"locations_{ingested_at.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    )
    
    output_path = RAW_DATA_DIR / filename
    temp_path = output_path.with_suffix(".tmp")
    
    try:
        temp_path.write_text(
            json.dumps(envelope, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(output_path)
        
    except OSError:
        temp_path.unlink(missing_ok=True)
        logger.exception("Unable to save OpenAQ locations")
        raise
    
    return output_path

def run_location_discovery() -> tuple[Path, list[dict]]:
    logger.info("Starting OpenAQ location discovery")
    
    locations = get_locations()
    output_path = save_raw_locations(locations)
    
    sensors = extract_sensor_summary(locations)
    
    logger.info(
        "Discovered %s locations and %s sensors",
        len(locations),
        len(sensors),
    )
    
    return output_path, sensors