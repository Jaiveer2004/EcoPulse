import random
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from ecopulse.models.sensor_event import SensorEvent

STATION = {
    "location_id": 9001,
    "location_name": "EcoPulse Synthetic Station - Patiala",
    "latitude": 30.3398,
    "longitude": 76.3869,
}

SENSORS = [
    {
        "sensor_id": 900001,
        "parameter": "pm25",
        "unit": "µg/m³",
        "baseline": 45.0,
        "variation": 15.0,
    },
    {
        "sensor_id": 900002,
        "parameter": "pm10",
        "unit": "µg/m³",
        "baseline": 90.0,
        "variation": 25.0,
    },
]


def generate_event(
    sensor: dict,
    observed_at: datetime,
    rng: random.Random,
) -> SensorEvent:
    """Generate and validate one synthetic sensor event."""

    value = rng.gauss(
        sensor["baseline"],
        sensor["variation"],
    )

    # Concentrations cannot be negative.
    value = max(0.0, round(value, 2))

    event_id = str(uuid.uuid4())
    ingested_at = datetime.now(UTC)

    event_data = {
        "event_id": event_id,
        "schema_version": "1.0",
        "sensor_id": sensor["sensor_id"],
        "location_id": STATION["location_id"],
        "location_name": STATION["location_name"],
        "parameter": sensor["parameter"],
        "value": value,
        "unit": sensor["unit"],
        "observed_at": observed_at,
        "ingested_at": ingested_at,
        "latitude": STATION["latitude"],
        "longitude": STATION["longitude"],
        "source_type": "synthetic",
        "source_name": "ecopulse_sensor_simulator",
        "source_record_id": event_id,
    }

    return SensorEvent.model_validate(event_data)


def generate_batch(
    count: int,
    seed: int | None = None,
) -> list[SensorEvent]:
    """Generate a batch of timestamped events."""

    if count <= 0:
        raise ValueError("Event count must be greater than zero")

    rng = random.Random(seed)

    events = []

    start_time = datetime.now(UTC) - timedelta(minutes=count - 1)

    for index in range(count):
        observed_at = start_time + timedelta(minutes=index)

        # Generate one reading from each sensor per interval.
        for sensor in SENSORS:
            event = generate_event(
                sensor=sensor,
                observed_at=observed_at,
                rng=rng,
            )

            events.append(event)

    return events


def save_events(
    events: list[SensorEvent],
    output_dir: Path,
) -> Path:
    """Persist generated events in JSON Lines format."""

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    output_path = output_dir / f"sensor_events_{timestamp}.jsonl"

    with output_path.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(event.model_dump_json() + "\n")

    return output_path
