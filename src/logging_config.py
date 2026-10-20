"""Logging configuration shared by API and worker."""

import logging


def configure_logging() -> None:
    """Configure the root logger with a consistent format and INFO level."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
