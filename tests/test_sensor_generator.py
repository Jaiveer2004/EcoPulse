import pytest
from pydantic import ValidationError

from ecopulse.models.sensor_event import SensorEvent
from ecopulse.simulation.sensor_generator import generate_batch


def test_generate_batch_count():
    events = generate_batch(count=5, seed=42)

    assert len(events) == 10


def test_generated_events_are_pydantic_models():
    events = generate_batch(count=3, seed=42)

    assert all(isinstance(event, SensorEvent) for event in events)


def test_generated_events_have_synthetic_provenance():
    events = generate_batch(count=3, seed=42)

    assert all(event.source_type == "synthetic" for event in events)
    assert all(event.source_name == "ecopulse_sensor_simulator" for event in events)


def test_generated_events_have_unique_ids():
    events = generate_batch(count=10, seed=42)

    event_ids = [event.event_id for event in events]

    assert len(event_ids) == len(set(event_ids))


def test_same_seed_generates_same_measurements():
    first = generate_batch(count=5, seed=42)
    second = generate_batch(count=5, seed=42)

    first_values = [(event.sensor_id, event.value) for event in first]

    second_values = [(event.sensor_id, event.value) for event in second]

    assert first_values == second_values


def test_generated_events_use_expected_sensors():
    events = generate_batch(count=5, seed=42)

    sensor_ids = {event.sensor_id for event in events}

    assert sensor_ids == {900001, 900002}


def test_zero_intervals_are_rejected():
    with pytest.raises(ValueError):
        generate_batch(count=0)


def test_negative_pm25_is_rejected():
    with pytest.raises(ValidationError):
        SensorEvent.model_validate(
            {
                "event_id": "test-event",
                "schema_version": "1.0",
                "sensor_id": 900001,
                "location_id": 9001,
                "location_name": "EcoPulse Synthetic Station - Patiala",
                "parameter": "pm25",
                "value": -10,
                "unit": "µg/m³",
                "observed_at": "2026-11-26T10:00:00+00:00",
                "ingested_at": "2026-11-26T10:00:01+00:00",
                "latitude": 30.3398,
                "longitude": 76.3869,
                "source_type": "synthetic",
                "source_name": "ecopulse_sensor_simulator",
                "source_record_id": "test-event",
            }
        )
