import psycopg
from psycopg.rows import dict_row

from ecopulse.config import get_database_config
from ecopulse.logging_config import get_logger

logger = get_logger(__name__)


def connect_db() -> psycopg.Connection:
    """
    Establish a PostgreSQL connection.

    Raises psycopg.OperationalError if the database
    cannot be reached or authentication fails.
    """

    try:
        config = get_database_config()

        connection = psycopg.connect(
            **config,
            row_factory=dict_row,
        )

        logger.info("PostgreSQL connection established")

        return connection

    except psycopg.OperationalError:
        logger.exception("Unable to establish PostgreSQL connection")
        raise

    except RuntimeError:
        logger.exception("Database configuration is invalid")
        raise
