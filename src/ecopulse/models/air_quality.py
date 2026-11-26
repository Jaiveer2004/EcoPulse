from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AirQualityRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    sensor_id: int = Field(gt=0)
    location_id: int = Field(gt=0)
    location_name: str = Field(min_length=1)

    parameter: str = Field(min_length=1)
    value: float = Field(ge=0)
    unit: str = Field(min_length=1)

    observed_at: datetime
    ingested_at: datetime

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    source_type: str = Literal["real", "synthetic"]
    source_name: str = Literal["openaq"]

    source_record_id: None = None

    @field_validator("observed_at", "ingested_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include timezone information")

        return value
