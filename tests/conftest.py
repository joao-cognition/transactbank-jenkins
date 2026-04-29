"""Shared test fixtures."""

import pytest

from app.extensions import db as _db
from app.factory import create_app
from app.models.account import Account


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    app = create_app("testing")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return app


@pytest.fixture(scope="function")
def db(app):
    """Create a fresh database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_accounts(db):
    """Create sample accounts for testing."""
    account_a = Account(
        holder_name="Alice Johnson",
        email="alice@example.com",
        account_type="checking",
        balance=1000.00,
        currency="USD",
    )
    account_b = Account(
        holder_name="Bob Smith",
        email="bob@example.com",
        account_type="savings",
        balance=500.00,
        currency="USD",
    )
    db.session.add_all([account_a, account_b])
    db.session.commit()
    return account_a, account_b
