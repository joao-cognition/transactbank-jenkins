"""Unit tests for account endpoints."""

import json


class TestAccountEndpoints:
    """Test account CRUD operations."""

    def test_list_accounts_empty(self, client):
        """Should return empty list when no accounts exist."""
        response = client.get("/api/v1/accounts")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["total"] == 0
        assert data["accounts"] == []

    def test_create_account(self, client):
        """Should create a new account successfully."""
        payload = {
            "holder_name": "Jane Doe",
            "email": "jane@example.com",
            "account_type": "checking",
            "initial_deposit": 250.00,
        }
        response = client.post(
            "/api/v1/accounts",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["holder_name"] == "Jane Doe"
        assert data["balance"] == 250.00

    def test_create_account_invalid_email(self, client):
        """Should reject account with invalid email."""
        payload = {
            "holder_name": "Bad Email",
            "email": "not-an-email",
        }
        response = client.post(
            "/api/v1/accounts",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_get_account(self, client, sample_accounts):
        """Should return account details."""
        account_a, _ = sample_accounts
        response = client.get(f"/api/v1/accounts/{account_a.id}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["holder_name"] == "Alice Johnson"

    def test_get_account_not_found(self, client):
        """Should return 404 for non-existent account."""
        response = client.get("/api/v1/accounts/9999")
        assert response.status_code == 404

    def test_get_balance(self, client, sample_accounts):
        """Should return account balance."""
        account_a, _ = sample_accounts
        response = client.get(f"/api/v1/accounts/{account_a.id}/balance")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["balance"] == 1000.00

    def test_update_account(self, client, sample_accounts):
        """Should update account holder name."""
        account_a, _ = sample_accounts
        response = client.patch(
            f"/api/v1/accounts/{account_a.id}",
            data=json.dumps({"holder_name": "Alice Williams"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["holder_name"] == "Alice Williams"

    def test_list_accounts_filter_by_type(self, client, sample_accounts):
        """Should filter accounts by type."""
        response = client.get("/api/v1/accounts?type=savings")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["total"] == 1
        assert data["accounts"][0]["account_type"] == "savings"
