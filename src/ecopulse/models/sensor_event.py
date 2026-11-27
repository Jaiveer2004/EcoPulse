from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SensorEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    event_id: str = Field(min_length=1)
    schema_version: Literal["1.0"]

    sensor_id: int = Field(gt=0)
    location_id: int = Field(gt=0)
    location_name: str = Field(min_length=1)

    parameter: Literal["pm25", "pm10"]
    value: float = Field(ge=0)
    unit: Literal["µg/m³"]

    observed_at: datetime
    ingested_at: datetime

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    source_type: Literal["synthetic"]
    source_name: Literal["ecopulse_sensor_simulator"]

    source_record_id: str = Field(min_length=1)

    @field_validator("observed_at", "ingested_at")
    @classmethod
    def timestamps_must_be_timezone_aware(
        cls,
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include timezone information")

        return value

    @model_validator(mode="after")
    def validate_sensor_parameter(self):
        expected_sensor = {
            "pm25": 900001,
            "pm10": 900002,
        }

        if self.sensor_id != expected_sensor[self.parameter]:
            raise ValueError(
                f"{self.parameter} must use sensor {expected_sensor[self.parameter]}"
            )

        if self.parameter == "pm25" and self.value > 1000:
            raise ValueError("PM2.5 exceeds simulator safety range")

        if self.parameter == "pm10" and self.value > 2000:
            raise ValueError("PM10 exceeds simulator safety range")

        return self
