import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from dosaku.utils import ifnone


def formatter(fmt: Optional[str] = None, **kwargs) -> logging.Formatter:
    fmt = ifnone(fmt, default='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.Formatter(fmt, **kwargs)


def logger(
        name: str,
        logger_level: Optional[int] = logging.DEBUG,
        stream_level: Optional[int] = logging.WARN,
        stream_formatter: Optional[str] = None,
        file_level: Optional[int] = None,
        file_formatter: Optional[str] = None,
        file_name: str = 'logs.txt'
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logger_level)

    if stream_level is not None:
        fmt = ifnone(stream_formatter, default=formatter())
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(stream_level)
        stream_handler.setFormatter(fmt)
        logger.addHandler(stream_handler)

    if file_level is not None:
        fmt = ifnone(file_formatter, default=formatter())
        file_handler = logging.handlers.RotatingFileHandler(file_name)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    return logger

