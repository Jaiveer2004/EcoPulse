import os
from pathlib import Path

from dotenv import load_dotenv

# Locate the project-root .env file.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


def get_database_config() -> dict:
    """Return PostgreSQL connection settings from environment variables."""

    required_variables = [
        "POSTGRES_HOST",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing = [variable for variable in required_variables if not os.getenv(variable)]

    if missing:
        raise RuntimeError(
            f"Misisng database environment variables: {', '.join(missing)}"
        )

    try:
        port = int(os.getenv("POSTGRES_PORT", "5432"))
    except ValueError as exec:
        raise RuntimeError("POSTGRES_PORT must be a valid integer") from exec

    if not 1 <= port <= 65535:
        raise RuntimeError("POSTGRES_PORT must be between 1 and 65535")

    return {
        "host": os.environ["POSTGRES_HOST"],
        "port": port,
        "dbname": os.environ["POSTGRES_DB"],
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
        "connect_timeout": 5,
    }
