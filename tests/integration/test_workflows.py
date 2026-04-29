"""Integration tests for end-to-end banking workflows."""

import json


class TestBankingWorkflows:
    """Test complete banking scenarios."""

    def test_full_transfer_workflow(self, client, sample_accounts):
        """End-to-end: create accounts, transfer, verify balances."""
        account_a, account_b = sample_accounts

        # Check initial balances
        resp_a = client.get(f"/api/v1/accounts/{account_a.id}/balance")
        assert json.loads(resp_a.data)["balance"] == 1000.00

        resp_b = client.get(f"/api/v1/accounts/{account_b.id}/balance")
        assert json.loads(resp_b.data)["balance"] == 500.00

        # Perform transfer
        tx_resp = client.post(
            "/api/v1/transactions",
            data=json.dumps({
                "source_account_id": account_a.id,
                "target_account_id": account_b.id,
                "amount": 200.00,
                "description": "Integration test transfer",
            }),
            content_type="application/json",
        )
        assert tx_resp.status_code == 201

        # Verify updated balances
        resp_a = client.get(f"/api/v1/accounts/{account_a.id}/balance")
        assert json.loads(resp_a.data)["balance"] == 800.00

        resp_b = client.get(f"/api/v1/accounts/{account_b.id}/balance")
        assert json.loads(resp_b.data)["balance"] == 700.00

    def test_transfer_and_reversal_workflow(self, client, sample_accounts):
        """End-to-end: transfer then reverse, balances should be restored."""
        account_a, account_b = sample_accounts

        # Perform transfer
        tx_resp = client.post(
            "/api/v1/transactions",
            data=json.dumps({
                "source_account_id": account_a.id,
                "target_account_id": account_b.id,
                "amount": 150.00,
            }),
            content_type="application/json",
        )
        tx_id = json.loads(tx_resp.data)["id"]

        # Reverse the transaction
        reverse_resp = client.post(f"/api/v1/transactions/{tx_id}/reverse")
        assert reverse_resp.status_code == 200

        # Verify balances are restored
        resp_a = client.get(f"/api/v1/accounts/{account_a.id}/balance")
        assert json.loads(resp_a.data)["balance"] == 1000.00

        resp_b = client.get(f"/api/v1/accounts/{account_b.id}/balance")
        assert json.loads(resp_b.data)["balance"] == 500.00

    def test_report_after_transactions(self, client, sample_accounts):
        """End-to-end: perform transactions and check summary report."""
        account_a, account_b = sample_accounts

        # Create multiple transactions
        for amount in [100.00, 200.00, 50.00]:
            client.post(
                "/api/v1/transactions",
                data=json.dumps({
                    "source_account_id": account_a.id,
                    "target_account_id": account_b.id,
                    "amount": amount,
                }),
                content_type="application/json",
            )

        # Check summary report
        resp = client.get("/api/v1/reports/summary")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["total_transactions"] == 3
        assert data["completed_volume"] == 350.00
