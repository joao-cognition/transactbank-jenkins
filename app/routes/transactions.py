"""Transaction endpoints."""

from flask import Blueprint, jsonify, request

from app.extensions import limiter
from app.models.transaction import Transaction
from app.schemas import TransactionSchema
from app.services.transaction_service import TransactionService

transactions_bp = Blueprint("transactions", __name__)
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)


@transactions_bp.route("/transactions", methods=["GET"])
@limiter.limit("30/minute")
def list_transactions():
    """List transactions with filtering and pagination."""
    status = request.args.get("status")
    tx_type = request.args.get("type")
    account_id = request.args.get("account_id", type=int)

    query = Transaction.query
    if status:
        query = query.filter_by(status=status)
    if tx_type:
        query = query.filter_by(transaction_type=tx_type)
    if account_id:
        query = query.filter(
            (Transaction.source_account_id == account_id)
            | (Transaction.target_account_id == account_id)
        )

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = query.order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "transactions": transactions_schema.dump(pagination.items),
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages,
    }), 200


@transactions_bp.route("/transactions/<int:tx_id>", methods=["GET"])
@limiter.limit("60/minute")
def get_transaction(tx_id: int):
    """Get transaction details."""
    tx = Transaction.query.get_or_404(tx_id)
    return jsonify(transaction_schema.dump(tx)), 200


@transactions_bp.route("/transactions", methods=["POST"])
@limiter.limit("20/minute")
def create_transaction():
    """Initiate a new transaction."""
    data = request.get_json()
    errors = transaction_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        tx = TransactionService.transfer(
            source_account_id=data["source_account_id"],
            target_account_id=data["target_account_id"],
            amount=data["amount"],
            currency=data.get("currency", "USD"),
            description=data.get("description"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(transaction_schema.dump(tx)), 201


@transactions_bp.route("/transactions/<int:tx_id>/reverse", methods=["POST"])
@limiter.limit("5/minute")
def reverse_transaction(tx_id: int):
    """Reverse a completed transaction."""
    try:
        tx = TransactionService.reverse(tx_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(transaction_schema.dump(tx)), 200
