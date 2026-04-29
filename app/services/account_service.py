"""Account business logic."""

from decimal import Decimal

from app.extensions import db
from app.models.account import Account


class AccountService:
    """Service layer for account operations."""

    @staticmethod
    def create_account(
        holder_name: str,
        email: str,
        account_type: str = "checking",
        currency: str = "USD",
        initial_deposit: float = 0,
    ) -> Account:
        """Create a new bank account.

        Args:
            holder_name: Full name of the account holder.
            email: Contact email address.
            account_type: Type of account (checking, savings, business).
            currency: ISO 4217 currency code.
            initial_deposit: Initial deposit amount.

        Returns:
            Newly created Account instance.
        """
        account = Account(
            holder_name=holder_name,
            email=email,
            account_type=account_type,
            currency=currency,
            balance=Decimal(str(initial_deposit)),
        )
        db.session.add(account)
        db.session.commit()
        return account

    @staticmethod
    def get_account(account_id: int) -> Account:
        """Retrieve an account by ID.

        Args:
            account_id: Database primary key.

        Returns:
            Account instance.

        Raises:
            ValueError: If account not found or inactive.
        """
        account = Account.query.get(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        if not account.is_active:
            raise ValueError(f"Account {account_id} is inactive")
        return account

    @staticmethod
    def deactivate_account(account_id: int) -> Account:
        """Deactivate a bank account.

        Args:
            account_id: Database primary key.

        Returns:
            Updated Account instance.
        """
        account = AccountService.get_account(account_id)
        account.is_active = False
        db.session.commit()
        return account
