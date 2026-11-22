from src.ecopulse.database import connect_db


def test_postgres_connection():
    with connect_db() as connection:
        result = connection.execute("SELECT 1 as health").fetchone()

        assert result["health"] == 1


def test_station_exist():
    with connect_db() as connection:
        result = connection.execute(
            """
            SELECT station_code
            FROM core.stations
            WHERE station_code = %s
            """,
            ("SYNTH-TEST-001",),
        ).fetchone()

        assert result is not None
        assert result["station_code"] == "SYNTH-TEST-001"
