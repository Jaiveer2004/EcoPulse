import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


@dataclass(frozen=True)
class SourceConfig:
    region: str
    country: str
    longitude: str
    latitude: str
    search_radius: int
    openaq_api_key: str
    openaq_base_url: str
    openmeteo_base_url: str


def get_source_config() -> SourceConfig:
    try:
        latitude = float(os.getenv("ECOPULSE_LATITUDE", "30.3398"))
        longitude = float(os.getenv("ECOPULSE_LONGITUDE", "76.3869"))
        search_radius = int(os.getenv("ECOPULSE_SEARCH_RADIUS", "25000"))
    except ValueError as exc:
        raise ValueError("Invalid numeric environmental configuration") from exc

    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")

    if search_radius <= 0:
        raise ValueError("Search radius must be positive")

    return SourceConfig(
        region=os.getenv("ECOPULSE_REGION", "Patiala"),
        country=os.getenv("ECOPULSE_COUNTRY", "India"),
        latitude=latitude,
        longitude=longitude,
        search_radius=search_radius,
        openaq_api_key=os.getenv("OPENAQ_API_KEY", "").strip(),
        openaq_base_url=os.getenv(
            "OPENAQ_BASE_URL",
            "https://api.openaq.org/v3",
        ).rstrip("/"),
        openmeteo_base_url=os.getenv(
            "OPENMETEO_BASE_URL",
            "https://api.open-meteo.com/v1/forecast",
        ),
    )
