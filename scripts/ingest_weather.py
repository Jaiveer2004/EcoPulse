from ecopulse.ingestion.openmeteo import run_ingestion

def main() -> None:
    output_path = run_ingestion()
    
    print("\nWeather ingestion successful!")
    print(f"Raw data file: {output_path}")

if __name__ == "__main__":
    main()