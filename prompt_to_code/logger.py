import logging
import os
import tempfile
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path

DEFAULT_LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"


def _create_log_directory(log_directory: str | None = None) -> Path:
    if log_directory is None:
        return Path(tempfile.gettempdir()) / "prompt-to-code" / "logs"
    return Path(log_directory)


@dataclass
class StreamLoggerConfig:
    level: int | None = logging.DEBUG
    format: str = DEFAULT_LOG_FORMAT
    enabled: bool = True


@dataclass
class FileLoggerConfig:
    level: int | None = logging.INFO
    format: str = DEFAULT_LOG_FORMAT
    enabled: bool = False
    maxBytes: int = 1000000
    backupCount: int = 5
    filename: str | None = None
    log_directory: str | Path | None = None

    def __post_init__(self):
        if self.filename is None:
            if self.enabled:
                self.filename = "prompt-to-code.log"
        else:
            self.enabled = True

        if self.enabled:
            self.log_directory = _create_log_directory(self.log_directory)


@dataclass
class LoggerConfig:
    stream: StreamLoggerConfig
    file: FileLoggerConfig


def make_stream_handler(config: StreamLoggerConfig) -> logging.StreamHandler:
    formatter = logging.Formatter(config.format)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(config.level)
    stream_handler.setFormatter(formatter)
    return stream_handler


def make_file_handler(config: FileLoggerConfig) -> logging.FileHandler:
    formatter = logging.Formatter(config.format)

    config.log_directory = _create_log_directory(config.log_directory)
    if not config.log_directory.exists():
        os.makedirs(config.log_directory, exist_ok=True)

    file_handler = RotatingFileHandler(
        config.log_directory / config.filename,
        maxBytes=config.maxBytes,
        backupCount=config.backupCount,
    )
    file_handler.setLevel(config.level)
    file_handler.setFormatter(formatter)
    return file_handler


def create_logger(config: LoggerConfig, name: str = "prompt-to-code") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if config.stream.enabled:
        logger.addHandler(make_stream_handler(config.stream))
        logger.debug("Stream logger enabled")
    if config.file.enabled:
        logger.addHandler(make_file_handler(config.file))
        logger.debug("File logger enabled")
    return logger
