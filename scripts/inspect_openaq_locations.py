import json
from pathlib import Path


RAW_DIR = Path("data/raw/openaq")

SENSOR_IDS = [15243, 12235142, 15260, 12235141]


def find_sensor_locations(data, sensor_id):
    """Find a location containing the requested sensor."""

    if isinstance(data, dict):
        sensors = data.get("sensors", [])

        if isinstance(sensors, list):
            for sensor in sensors:
                if isinstance(sensor, dict) and sensor.get("id") == sensor_id:
                    return {
                        "location_id": data.get("id"),
                        "location_name": data.get("name"),
                        "coordinates": data.get("coordinates"),
                        "sensor": sensor,
                    }

        for value in data.values():
            result = find_sensor_locations(value, sensor_id)
            if result:
                return result

    elif isinstance(data, list):
        for item in data:
            result = find_sensor_locations(item, sensor_id)
            if result:
                return result

    return None


def main():
    files = sorted(RAW_DIR.glob("locations_*.json"))

    if not files:
        raise FileNotFoundError("No OpenAQ location discovery file found.")

    latest_file = files[-1]
    data = json.loads(latest_file.read_text(encoding="utf-8"))

    print(f"Using: {latest_file.name}\n")

    for sensor_id in SENSOR_IDS:
        result = find_sensor_locations(data, sensor_id)

        print(f"Sensor ID: {sensor_id}")

        if result:
            print(f"Location ID: {result['location_id']}")
            print(f"Location name: {result['location_name']}")
            print(f"Coordinates: {result['coordinates']}")
        else:
            print("Location metadata not found.")

        print("-" * 40)


if __name__ == "__main__":
    main()