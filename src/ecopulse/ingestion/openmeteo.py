import json
from datetime import UTC, datetime
from pathlib import Path

import httpx

from ecopulse.logging_config import configure_logging, get_logger
from ecopulse.source_config import get_source_config

configure_logging()
logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "openmeteo"

WEATHER_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
]


class OpenMeteoIngestionError(Exception):
    """Raised when Open-Meteo ingestion fails."""


def fetch_weather() -> dict:
    config = get_source_config()

    params = {
        "latitude": config.latitude,
        "longitude": config.longitude,
        "hourly": ",".join(WEATHER_VARIABLES),
        "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    }

    logger.info(
        "Requesting weather data for %s, %s",
        config.region,
        config.country,
    )

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.get(
                config.openmeteo_base_url,
                params=params,
            )
            response.raise_for_status()

        payload = response.json()

    except httpx.TimeoutException as exc:
        logger.exception(
            "Open-Meteo returned HTTP status %s",
            exc.response.status_code,
        )
        raise OpenMeteoIngestionError(
            f"Weather API returned HTTP {exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        logger.exception("Unable to connect to Open-Meteo")
        raise OpenMeteoIngestionError("Weather API connection failed") from exc

    except ValueError as exc:
        logger.exception("Invalid JSON response")
        raise OpenMeteoIngestionError("Weather API returned invalid JSON") from exc

    if not isinstance(payload, dict):
        raise OpenMeteoIngestionError("Unexpected API response format")

    if payload.get("error"):
        raise OpenMeteoIngestionError(
            f"Open-Meteo API error: {payload.get('reason', 'Unknown error')}"
        )

    hourly = payload.get("hourly")

    if not isinstance(hourly, dict):
        raise OpenMeteoIngestionError("Missing or invalid hourly data")

    times = hourly.get("time")

    if not isinstance(times, list) or not times:
        raise OpenMeteoIngestionError("Hourly timestamps are missing")

    for variable in WEATHER_VARIABLES:
        values = hourly.get(variable)

        if not isinstance(values, list) or len(values) != len(times):
            raise OpenMeteoIngestionError(
                f"Invalid or missing weather variable: {variable}"
            )
            
    logger.info(
        "Successfully fetched %d hourly weather records",
        len(times),
    )
    
    return payload

def save_raw_weather(payload: dict) -> Path:
    config = get_source_config()
    
    ingested_at = datetime.now(UTC)
    
    envelope = {
        "source_type": "real",
        "source_name": "open_meteo",
        "data_kind": "forecast",
        "time_semantics": "valid_time",
        "region": config.region,
        "country": config.country,
        "requested_coordinates": {
            "latitude": config.latitude,
            "longitude": config.longitude,
        },
        "ingest_at": ingested_at.isoformat(),
        "raw_payload": payload,
    }
    
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    filename = (
        f"weather_{ingested_at.strftime('%Y%m%dT%H%M%S%fZ')}.json"
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
        logger.exception("Unable to save raw weather data")
        raise
    
    logger.info("Raw weather data saved to %s", output_path)
    
    return output_path

def run_ingestion() -> Path:
    logger.info("Starting Open-Meteo ingestion")
    
    payload = fetch_weather()
    output_path = save_raw_weather(payload)
    
    logger.info("Open-Meteo ingestion completed")
    
    return output_path