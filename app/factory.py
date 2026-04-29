"""Application factory."""

import logging
import os

from flask import Flask

from app.config import config_by_name
from app.extensions import cors, db, limiter, ma, migrate


def create_app(config_name: str = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: Configuration environment name.

    Returns:
        Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    _init_extensions(app)
    _register_blueprints(app)
    _configure_logging(app)

    return app


def _init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])
    limiter.init_app(app)


def _register_blueprints(app: Flask) -> None:
    """Register application blueprints."""
    from app.routes.accounts import accounts_bp
    from app.routes.health import health_bp
    from app.routes.reports import reports_bp
    from app.routes.transactions import transactions_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(accounts_bp, url_prefix="/api/v1")
    app.register_blueprint(transactions_bp, url_prefix="/api/v1")
    app.register_blueprint(reports_bp, url_prefix="/api/v1")


def _configure_logging(app: Flask) -> None:
    """Configure application logging."""
    log_level = getattr(logging, app.config["LOG_LEVEL"].upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
