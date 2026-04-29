"""Transaction model."""

import uuid
from datetime import datetime, timezone

from app.extensions import db


class Transaction(db.Model):
    """Banking transaction entity."""

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(
        db.String(36), unique=True, nullable=False,
        default=lambda: str(uuid.uuid4())
    )
    source_account_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id"), nullable=False
    )
    target_account_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id"), nullable=False
    )
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="USD")
    transaction_type = db.Column(
        db.String(20), nullable=False, default="transfer"
    )
    status = db.Column(db.String(20), nullable=False, default="pending")
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    processed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Transaction {self.reference} ({self.status})>"
