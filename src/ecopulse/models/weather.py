from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class WeatherRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    
    parameter: Literal[
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
    ]
    
    value: float
    unit: str = Field(min_length=1)
    
    valid_at: datetime
    ingested_at: datetime
    
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    
    region: str = Field(min_length=1)
    country: str = Field(min_length=1)
    
    source_type: Literal["real", "synthetic"]
    source_name: Literal["open_meteo"]
    
    data_kind: Literal["forecast"]
    time_semantics: Literal["valid_time"]
    
    @field_validator("valid_at", "ingested_at")
    @classmethod
    def timestamps_must_be_timezone_aware(
            cls,
            value: datetime
        ) -> datetime:
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError ("Timestamp must include timezone information")
            
            return value
        
    @model_validator(mode="after")
    def validate_weather_value(self):
        if self.parameter == "temperature_2m":
            if not -90 <= self.value <= 65:
                raise ValueError(
                    "temperature_2m must be between -90 and 65"
                )
            
        elif self.parameter == "relative_humidity_2m":
            if not 0 <= self.value <= 100:
                raise ValueError(
                    "relative_humidity_2m must be between 0 and 100"
                )
                
        elif self.parameter in {"precipitation", "wind_speed_10m"}:
            if self.value < 0:
                raise ValueError(
                    f"{self.parameter} cannot be negative"
                )
        
        return self