"""Account model."""

import uuid
from datetime import datetime, timezone

from app.extensions import db


class Account(db.Model):
    """Bank account entity."""

    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(
        db.String(20), unique=True, nullable=False,
        default=lambda: f"ACC-{uuid.uuid4().hex[:12].upper()}"
    )
    holder_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    account_type = db.Column(
        db.String(20), nullable=False, default="checking"
    )
    balance = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    currency = db.Column(db.String(3), nullable=False, default="USD")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    transactions_sent = db.relationship(
        "Transaction",
        foreign_keys="Transaction.source_account_id",
        backref="source_account",
        lazy="dynamic",
    )
    transactions_received = db.relationship(
        "Transaction",
        foreign_keys="Transaction.target_account_id",
        backref="target_account",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Account {self.account_number} ({self.holder_name})>"
