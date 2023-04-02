import logging

FORMATTER: str = (
    '%(asctime)s - %(levelname)s - %(name)s - (%(filename)s).%(funcName)s'
    + '(%(lineno)d) - %(message)s'
)

logging.basicConfig(level=logging.INFO, format=FORMATTER)


def get_logger(name: str) -> logging.Logger:
    """Создает логгер."""
    return logging.getLogger(name)
