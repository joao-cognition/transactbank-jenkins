"""Account management endpoints."""

from flask import Blueprint, jsonify, request

from app.extensions import db, limiter
from app.models.account import Account
from app.schemas import AccountSchema
from app.services.account_service import AccountService

accounts_bp = Blueprint("accounts", __name__)
account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)


@accounts_bp.route("/accounts", methods=["GET"])
@limiter.limit("30/minute")
def list_accounts():
    """List all accounts with optional filtering."""
    account_type = request.args.get("type")
    is_active = request.args.get("active")

    query = Account.query
    if account_type:
        query = query.filter_by(account_type=account_type)
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == "true")

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "accounts": accounts_schema.dump(pagination.items),
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages,
    }), 200


@accounts_bp.route("/accounts/<int:account_id>", methods=["GET"])
@limiter.limit("60/minute")
def get_account(account_id: int):
    """Get account details by ID."""
    account = Account.query.get_or_404(account_id)
    return jsonify(account_schema.dump(account)), 200


@accounts_bp.route("/accounts", methods=["POST"])
@limiter.limit("10/minute")
def create_account():
    """Create a new bank account."""
    data = request.get_json()
    errors = account_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    account = AccountService.create_account(
        holder_name=data["holder_name"],
        email=data["email"],
        account_type=data.get("account_type", "checking"),
        currency=data.get("currency", "USD"),
        initial_deposit=data.get("initial_deposit", 0),
    )

    return jsonify(account_schema.dump(account)), 201


@accounts_bp.route("/accounts/<int:account_id>", methods=["PATCH"])
@limiter.limit("10/minute")
def update_account(account_id: int):
    """Update account details."""
    account = Account.query.get_or_404(account_id)
    data = request.get_json()

    if "holder_name" in data:
        account.holder_name = data["holder_name"]
    if "email" in data:
        account.email = data["email"]
    if "is_active" in data:
        account.is_active = data["is_active"]

    db.session.commit()
    return jsonify(account_schema.dump(account)), 200


@accounts_bp.route("/accounts/<int:account_id>/balance", methods=["GET"])
@limiter.limit("60/minute")
def get_balance(account_id: int):
    """Get current account balance."""
    account = Account.query.get_or_404(account_id)
    return jsonify({
        "account_number": account.account_number,
        "balance": float(account.balance),
        "currency": account.currency,
    }), 200
