from ecopulse.ingestion.openaq import run_location_discovery


def main() -> None:
    output_path, sensors = run_location_discovery()

    print("\nOpenAQ discovery completed!")
    print(f"Raw location data: {output_path}")
    print(f"Total sensors discovered: {len(sensors)}")

    print("\nAvailable sensors:")

    for sensor in sensors:
        print(
            f"Location: {sensor['location_name']} | "
            f"Parameter: {sensor['parameter']} | "
            f"Sensor ID: {sensor['sensor_id']} | "
            f"Unit: {sensor['unit']}"
        )


if __name__ == "__main__":
    main()
