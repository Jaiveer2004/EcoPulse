from ecopulse.ingestion.openaq_measurements import run_measurement_ingestion


def main() -> None:
    output_files = run_measurement_ingestion()

    print("\nAir-quality ingestion completed!")
    print(f"Sensor files generated: {len(output_files)}")

    for output_file in output_files:
        print(output_file)


if __name__ == "__main__":
    main()
