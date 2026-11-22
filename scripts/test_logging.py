from ecopulse.logging_config import configure_logging, get_logger


def main():
    configure_logging()

    logger = get_logger("ecopulse.test")

    logger.debug("Debug message")
    logger.info("EcoPulse started")
    logger.warning("Synthetic data detected")
    logger.error("Example error message")


if __name__ == "__main__":
    main()
