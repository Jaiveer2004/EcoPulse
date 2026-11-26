
# EcoPulse Synthetic Sensor Simulator

## Purpose

Generate controlled environmental sensor events for
streaming pipeline development and testing.

## Simulated station

- Location ID: 9001
- Name: EcoPulse Synthetic Station - Patiala
- Latitude: 30.3398
- Longitude: 76.3869

## Simulated sensors

| Sensor ID | Parameter | Unit |
|---|---|---|
| 900001 | PM2.5 | µg/m³ |
| 900002 | PM10 | µg/m³ |

## Event format

- JSON Lines (JSONL)
- Schema version: 1.0
- Unique event ID
- Observation timestamp
- Ingestion timestamp
- Explicit synthetic provenance

## Validation

Every generated event is validated using the
Pydantic SensorEvent model.

## Reproducibility

An optional random seed makes measurement values
reproducible for controlled tests.

UUIDs and generation timestamps remain unique
between runs.

## Important distinction

Synthetic events are not real environmental
observations and must not be presented as such.

## Future integration

Stage 2 will introduce Kafka producers and publish
these events to dedicated sensor-event topics.
