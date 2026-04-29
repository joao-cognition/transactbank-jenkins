"""Unit tests for transaction endpoints."""

import json


class TestTransactionEndpoints:
    """Test transaction operations."""

    def test_create_transaction(self, client, sample_accounts):
        """Should create a successful transfer."""
        account_a, account_b = sample_accounts
        payload = {
            "source_account_id": account_a.id,
            "target_account_id": account_b.id,
            "amount": 100.00,
            "description": "Test transfer",
        }
        response = client.post(
            "/api/v1/transactions",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["status"] == "completed"
        assert data["amount"] == 100.00

    def test_create_transaction_insufficient_funds(self, client, sample_accounts):
        """Should reject transfer with insufficient funds."""
        account_a, account_b = sample_accounts
        payload = {
            "source_account_id": account_a.id,
            "target_account_id": account_b.id,
            "amount": 999999.00,
        }
        response = client.post(
            "/api/v1/transactions",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_transaction_same_account(self, client, sample_accounts):
        """Should reject self-transfer."""
        account_a, _ = sample_accounts
        payload = {
            "source_account_id": account_a.id,
            "target_account_id": account_a.id,
            "amount": 50.00,
        }
        response = client.post(
            "/api/v1/transactions",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_list_transactions(self, client, sample_accounts):
        """Should list transactions."""
        account_a, account_b = sample_accounts
        # Create a transaction first
        payload = {
            "source_account_id": account_a.id,
            "target_account_id": account_b.id,
            "amount": 50.00,
        }
        client.post(
            "/api/v1/transactions",
            data=json.dumps(payload),
            content_type="application/json",
        )

        response = client.get("/api/v1/transactions")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["total"] >= 1

    def test_reverse_transaction(self, client, sample_accounts):
        """Should reverse a completed transaction."""
        account_a, account_b = sample_accounts
        payload = {
            "source_account_id": account_a.id,
            "target_account_id": account_b.id,
            "amount": 100.00,
        }
        create_resp = client.post(
            "/api/v1/transactions",
            data=json.dumps(payload),
            content_type="application/json",
        )
        tx_id = json.loads(create_resp.data)["id"]

        reverse_resp = client.post(f"/api/v1/transactions/{tx_id}/reverse")
        assert reverse_resp.status_code == 200
        data = json.loads(reverse_resp.data)
        assert data["status"] == "completed"
