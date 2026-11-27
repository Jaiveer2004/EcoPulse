import pytest
from pydantic import ValidationError

from ecopulse.models.air_quality import AirQualityRecord
from ecopulse.models.weather import WeatherRecord


def valid_air_record():
    return {
        "location_name": "Model Town, Patiala - PPCB",
        "sensor_id": 15243,
        "location_id": 5544,
        "parameter": "pm25",
        "value": 42.5,
        "unit": "µg/m³",
        "observed_at": "2026-11-16T14:15:00+00:00",
        "latitude": 30.349388,
        "longitude": 76.366642,
        "source_type": "real",
        "source_name": "openaq",
        "ingested_at": "2026-11-23T14:15:51.387248+00:00",
        "source_record_id": None,
    }


def valid_weather_record():
    return {
        "parameter": "temperature_2m",
        "value": 24.5,
        "unit": "°C",
        "valid_at": "2026-11-26T12:00:00+00:00",
        "latitude": 30.3398,
        "longitude": 76.3869,
        "region": "Patiala",
        "country": "India",
        "source_type": "real",
        "source_name": "open_meteo",
        "ingested_at": "2026-11-26T10:00:00+00:00",
        "data_kind": "forecast",
        "time_semantics": "valid_time",
    }


def test_valid_air_record():
    result = AirQualityRecord.model_validate(valid_air_record())

    assert result.sensor_id == 15243
    assert result.value == 42.5


def test_negative_air_quality_value_is_rejected():
    record = valid_air_record()
    record["value"] = -5

    with pytest.raises(ValidationError):
        AirQualityRecord.model_validate(record)


def test_invalid_air_quality_coordinates_are_rejected():
    record = valid_air_record()
    record["latitude"] = 120

    with pytest.raises(ValidationError):
        AirQualityRecord.model_validate(record)


def test_naive_air_timestamp_is_rejected():
    record = valid_air_record()
    record["observed_at"] = "2026-11-26T10:00:00"

    with pytest.raises(ValidationError):
        AirQualityRecord.model_validate(record)


def test_valid_weather_record():
    result = WeatherRecord.model_validate(valid_weather_record())

    assert result.parameter == "temperature_2m"
    assert result.value == 24.5


def test_negative_temperature_is_allowed():
    record = valid_weather_record()
    record["value"] = -5.0

    result = WeatherRecord.model_validate(record)

    assert result.value == -5.0


def test_humidity_above_100_is_rejected():
    record = valid_weather_record()
    record["parameter"] = "relative_humidity_2m"
    record["value"] = 150

    with pytest.raises(ValidationError):
        WeatherRecord.model_validate(record)


def test_negative_precipitation_is_rejected():
    record = valid_weather_record()
    record["parameter"] = "precipitation"
    record["value"] = -2

    with pytest.raises(ValidationError):
        WeatherRecord.model_validate(record)


def test_wrong_forecast_semantics_are_rejected():
    record = valid_weather_record()
    record["time_semantics"] = "observation_time"

    with pytest.raises(ValidationError):
        WeatherRecord.model_validate(record)


def test_unexpected_field_is_rejected():
    record = valid_air_record()
    record["unexpected_column"] = "surprise"

    with pytest.raises(ValidationError):
        AirQualityRecord.model_validate(record)


def test_nan_weather_value_is_rejected():
    record = valid_weather_record()
    record["value"] = float("nan")

    with pytest.raises(ValidationError):
        WeatherRecord.model_validate(record)
