import logging

from logger import setup_logging


def test_setup_logging_returns_named_logger() -> None:
    logger = setup_logging()
    assert logger.name == "Translator"
    assert isinstance(logger, logging.Logger)
