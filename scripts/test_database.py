from ecopulse.database import connect_db


def main():
    try:
        with connect_db() as connection:
            result = connection.execute(
                "SELECT version() AS database_version"
            ).fetchone()

            print("PostgreSQL connection successful!")
            print("Database version:", result["database_version"])

            station = connection.execute(
                """
                SELECT station_code, station_name, source_type
                FROM core.stations
                WHERE station_code = %s
                """,
                ("SYNTH-TEST-001",),
            ).fetchone()

            if station is None:
                print("Test station was not found.")
            else:
                print("\nStation retrieved successfully:")
                print(station)

    except Exception as error:
        print("Database connection or query failed.")
        print(f"Error type: {type(error).__name__}")
        print(f"Details: {error}")
        raise


if __name__ == "__main__":
    main()
