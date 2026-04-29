"""Marshmallow serialization schemas."""

from marshmallow import fields, validate

from app.extensions import ma


class AccountSchema(ma.Schema):
    """Account serialization schema."""

    id = fields.Integer(dump_only=True)
    account_number = fields.String(dump_only=True)
    holder_name = fields.String(
        required=True, validate=validate.Length(min=2, max=120)
    )
    email = fields.Email(required=True)
    account_type = fields.String(
        validate=validate.OneOf(["checking", "savings", "business"])
    )
    balance = fields.Float(dump_only=True)
    currency = fields.String(validate=validate.OneOf(["USD", "EUR", "GBP"]))
    is_active = fields.Boolean(dump_only=True)
    initial_deposit = fields.Float(load_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TransactionSchema(ma.Schema):
    """Transaction serialization schema."""

    id = fields.Integer(dump_only=True)
    reference = fields.String(dump_only=True)
    source_account_id = fields.Integer(required=True)
    target_account_id = fields.Integer(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    currency = fields.String(validate=validate.OneOf(["USD", "EUR", "GBP"]))
    transaction_type = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    description = fields.String(validate=validate.Length(max=255))
    created_at = fields.DateTime(dump_only=True)
    processed_at = fields.DateTime(dump_only=True)
