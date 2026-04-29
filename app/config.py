"""Application configuration for different environments."""

import os


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    RATE_LIMIT_DEFAULT = "100/hour"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    JWT_EXPIRATION_HOURS = 24


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://transactbank:transactbank@localhost:5432/transactbank_dev"
    )
    LOG_LEVEL = "DEBUG"


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://transactbank:transactbank@localhost:5432/transactbank_test"
    )
    RATE_LIMIT_DEFAULT = "1000/hour"


class StagingConfig(BaseConfig):
    """Staging configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    LOG_LEVEL = "WARNING"
    RATE_LIMIT_DEFAULT = "200/hour"


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    LOG_LEVEL = "ERROR"
    RATE_LIMIT_DEFAULT = "50/hour"
    JWT_EXPIRATION_HOURS = 8


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}
