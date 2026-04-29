"""Input validation helpers."""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format.

    Args:
        email: Email address to validate.

    Returns:
        True if the email format is valid.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_currency(code: str) -> bool:
    """Validate ISO 4217 currency code.

    Args:
        code: Three-letter currency code.

    Returns:
        True if the currency code is supported.
    """
    supported = {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"}
    return code.upper() in supported


def sanitize_string(value: str, max_length: int = 255) -> Optional[str]:
    """Sanitize and truncate a string input.

    Args:
        value: Raw input string.
        max_length: Maximum allowed length.

    Returns:
        Cleaned string, or None if input is empty.
    """
    if not value:
        return None
    cleaned = value.strip()
    cleaned = re.sub(r"[<>&\"']", "", cleaned)
    return cleaned[:max_length] if cleaned else None
