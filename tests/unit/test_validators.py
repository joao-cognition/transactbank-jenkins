"""Unit tests for utility validators."""

from app.utils.validators import sanitize_string, validate_currency, validate_email


class TestValidators:
    """Test input validation helpers."""

    def test_valid_email(self):
        assert validate_email("user@example.com") is True

    def test_invalid_email_no_at(self):
        assert validate_email("userexample.com") is False

    def test_invalid_email_no_domain(self):
        assert validate_email("user@") is False

    def test_valid_currency_usd(self):
        assert validate_currency("USD") is True

    def test_valid_currency_lowercase(self):
        assert validate_currency("eur") is True

    def test_invalid_currency(self):
        assert validate_currency("XYZ") is False

    def test_sanitize_string_strips_whitespace(self):
        assert sanitize_string("  hello  ") == "hello"

    def test_sanitize_string_removes_html(self):
        result = sanitize_string("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result

    def test_sanitize_string_truncates(self):
        long_str = "a" * 500
        result = sanitize_string(long_str, max_length=100)
        assert len(result) == 100

    def test_sanitize_empty_string(self):
        assert sanitize_string("") is None

    def test_sanitize_none(self):
        assert sanitize_string(None) is None
