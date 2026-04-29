"""Health check endpoints."""

from flask import Blueprint, jsonify

from app.extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Basic health check."""
    return jsonify({"status": "healthy", "service": "transactbank-api"}), 200


@health_bp.route("/health/ready", methods=["GET"])
def readiness_check():
    """Readiness probe — verifies database connectivity."""
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        return jsonify({"status": "not ready", "database": db_status}), 503

    return jsonify({"status": "ready", "database": db_status}), 200
