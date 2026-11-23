from ecopulse.source_config import get_source_config


def main() -> None:
    config = get_source_config()
    
    print("EcoPulse Source Configuration")
    print("-----------------------------")
    print(f"Region: {config.region}, {config.country}")
    print(f"Latitude: {config.latitude}")
    print(f"Longitude: {config.longitude}")
    print(f"Search radius: {config.search_radius} metres")
    print(f"OpenAQ API key configured: {bool(config.openaq_api_key)}")
    print(f"OpenAQ endpoint: {config.openaq_base_url}")
    print(f"Open-Meteo endpoint: {config.openmeteo_base_url}")
    
if __name__ == "__main__":
    main()