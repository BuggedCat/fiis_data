import logging
import sys

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        extra="allow",
    )


settings = Settings()  # type: ignore


def configure_logger(name="example", log_level=logging.INFO):
    """
    Configures and returns a logger.

    Args:
        name (str): Name of the logger.
        log_level (int): Minimum logging level to capture.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)

    # Avoid log messages being processed by ancestor loggers' handlers
    logger.propagate = False

    # Set the logger's level
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - [%(name)s:%(filename)s:%(funcName)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stdout = logging.StreamHandler(stream=sys.stdout)
    stdout.setFormatter(formatter)
    stdout.setLevel(log_level)

    logger.addHandler(stdout)

    return logger
