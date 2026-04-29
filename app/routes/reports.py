"""Reporting endpoints."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.extensions import db, limiter
from app.models.account import Account
from app.models.transaction import Transaction

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports/summary", methods=["GET"])
@limiter.limit("10/minute")
def transaction_summary():
    """Get transaction summary statistics."""
    total_accounts = db.session.query(func.count(Account.id)).scalar()
    active_accounts = db.session.query(
        func.count(Account.id)
    ).filter(Account.is_active.is_(True)).scalar()

    total_transactions = db.session.query(func.count(Transaction.id)).scalar()

    total_volume = db.session.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(Transaction.status == "completed").scalar()

    pending_count = db.session.query(
        func.count(Transaction.id)
    ).filter(Transaction.status == "pending").scalar()

    return jsonify({
        "total_accounts": total_accounts,
        "active_accounts": active_accounts,
        "total_transactions": total_transactions,
        "completed_volume": float(total_volume),
        "pending_transactions": pending_count,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }), 200


@reports_bp.route("/reports/daily", methods=["GET"])
@limiter.limit("5/minute")
def daily_report():
    """Get daily transaction report."""
    date_str = request.args.get("date")
    if date_str:
        try:
            report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    else:
        report_date = datetime.now(timezone.utc).date()

    transactions = Transaction.query.filter(
        func.date(Transaction.created_at) == report_date
    ).all()

    completed = [t for t in transactions if t.status == "completed"]
    failed = [t for t in transactions if t.status == "failed"]

    return jsonify({
        "date": report_date.isoformat(),
        "total_transactions": len(transactions),
        "completed": len(completed),
        "failed": len(failed),
        "total_volume": float(sum(t.amount for t in completed)),
        "average_amount": (
            float(sum(t.amount for t in completed) / len(completed))
            if completed else 0
        ),
    }), 200
