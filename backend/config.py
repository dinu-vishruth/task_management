"""Application configuration loaded from environment variables."""
import os
from datetime import timedelta
from pathlib import Path


class Config:
    """Base configuration."""

    # Use a long random key in production (e.g. openssl rand -hex 32).
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-only-32byte-key-change-in-prod!!",
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + str(Path(__file__).resolve().parent / "instance" / "app.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {"pool_pre_ping": True}
        if os.environ.get("DATABASE_URL", "").startswith("postgresql")
        else {}
    )

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_HOURS", "24"))
    )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
