"""Transaction business logic."""

from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db
from app.models.transaction import Transaction
from app.services.account_service import AccountService


class TransactionService:
    """Service layer for transaction operations."""

    @staticmethod
    def transfer(
        source_account_id: int,
        target_account_id: int,
        amount: float,
        currency: str = "USD",
        description: str = None,
    ) -> Transaction:
        """Execute a transfer between two accounts.

        Args:
            source_account_id: Sender account ID.
            target_account_id: Receiver account ID.
            amount: Transfer amount.
            currency: ISO 4217 currency code.
            description: Optional transaction description.

        Returns:
            Created Transaction instance.

        Raises:
            ValueError: If validation fails.
        """
        if source_account_id == target_account_id:
            raise ValueError("Source and target accounts must differ")

        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")

        source = AccountService.get_account(source_account_id)
        target = AccountService.get_account(target_account_id)

        if source.balance < amount_decimal:
            raise ValueError("Insufficient funds")

        if source.currency != target.currency:
            raise ValueError("Cross-currency transfers not supported")

        tx = Transaction(
            source_account_id=source_account_id,
            target_account_id=target_account_id,
            amount=amount_decimal,
            currency=currency,
            description=description,
            transaction_type="transfer",
            status="pending",
        )
        db.session.add(tx)

        source.balance -= amount_decimal
        target.balance += amount_decimal
        tx.status = "completed"
        tx.processed_at = datetime.now(timezone.utc)

        db.session.commit()
        return tx

    @staticmethod
    def reverse(transaction_id: int) -> Transaction:
        """Reverse a completed transaction.

        Args:
            transaction_id: ID of the transaction to reverse.

        Returns:
            New reversal Transaction instance.

        Raises:
            ValueError: If the original transaction cannot be reversed.
        """
        original = Transaction.query.get(transaction_id)
        if not original:
            raise ValueError(f"Transaction {transaction_id} not found")
        if original.status != "completed":
            raise ValueError("Only completed transactions can be reversed")

        return TransactionService.transfer(
            source_account_id=original.target_account_id,
            target_account_id=original.source_account_id,
            amount=float(original.amount),
            currency=original.currency,
            description=f"Reversal of {original.reference}",
        )
