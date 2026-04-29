#!/usr/bin/env python3
"""
Seed the database with test data for integration/smoke testing.

Usage:
    FLASK_ENV=testing python jenkins/scripts/seed_test_data.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.factory import create_app
from app.extensions import db
from app.models.account import Account
from app.models.transaction import Transaction


SEED_ACCOUNTS = [
    {
        "holder_name": "Alice Integration",
        "email": "alice@test.company.com",
        "account_type": "checking",
        "balance": 10000.00,
        "currency": "USD",
    },
    {
        "holder_name": "Bob Integration",
        "email": "bob@test.company.com",
        "account_type": "savings",
        "balance": 5000.00,
        "currency": "USD",
    },
    {
        "holder_name": "Charlie Integration",
        "email": "charlie@test.company.com",
        "account_type": "business",
        "balance": 25000.00,
        "currency": "USD",
    },
    {
        "holder_name": "Diana Integration",
        "email": "diana@test.company.com",
        "account_type": "checking",
        "balance": 750.00,
        "currency": "EUR",
    },
]


def seed():
    """Insert test data into the database."""
    app = create_app()

    with app.app_context():
        db.create_all()

        existing = Account.query.filter_by(email="alice@test.company.com").first()
        if existing:
            print("Test data already seeded. Skipping.")
            return

        for acct_data in SEED_ACCOUNTS:
            account = Account(**acct_data)
            db.session.add(account)

        db.session.commit()
        print(f"Seeded {len(SEED_ACCOUNTS)} test accounts.")

        accounts = Account.query.all()
        if len(accounts) >= 2:
            tx = Transaction(
                source_account_id=accounts[0].id,
                target_account_id=accounts[1].id,
                amount=100.00,
                currency="USD",
                transaction_type="transfer",
                status="completed",
                description="Seed transaction",
            )
            db.session.add(tx)
            db.session.commit()
            print("Seeded 1 test transaction.")


if __name__ == "__main__":
    seed()
