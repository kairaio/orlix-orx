from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEADERS = {"X-ORX-Admin-Key": "test-admin-key"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_orx_wallet_issue_and_transfer():
    account_a = client.post(
        "/api/v1/accounts",
        headers=HEADERS,
        json={
            "external_id": "TEST_USER_A",
            "display_name": "Test User A",
            "account_type": "human",
        },
    )
    assert account_a.status_code == 201, account_a.text
    wallet_a = account_a.json()["wallet"]["id"]

    account_b = client.post(
        "/api/v1/accounts",
        headers=HEADERS,
        json={
            "external_id": "TEST_USER_B",
            "display_name": "Test User B",
            "account_type": "human",
        },
    )
    assert account_b.status_code == 201, account_b.text
    wallet_b = account_b.json()["wallet"]["id"]

    issuance = client.post(
        "/api/v1/treasury/issue",
        headers={**HEADERS, "X-Idempotency-Key": "test-issue-001"},
        json={"to_wallet_id": wallet_a, "amount": "1000.00000000"},
    )
    assert issuance.status_code == 200, issuance.text

    transfer = client.post(
        "/api/v1/transactions/transfer",
        headers={**HEADERS, "X-Idempotency-Key": "test-transfer-001"},
        json={
            "from_wallet_id": wallet_a,
            "to_wallet_id": wallet_b,
            "amount": "250.00000000",
        },
    )
    assert transfer.status_code == 200, transfer.text

    balance_a = client.get(f"/api/v1/wallets/{wallet_a}/balance", headers=HEADERS)
    balance_b = client.get(f"/api/v1/wallets/{wallet_b}/balance", headers=HEADERS)
    assert balance_a.status_code == 200
    assert balance_b.status_code == 200
    assert balance_a.json()["balance"] == "750.00000000"
    assert balance_b.json()["balance"] == "250.00000000"

    duplicate = client.post(
        "/api/v1/transactions/transfer",
        headers={**HEADERS, "X-Idempotency-Key": "test-transfer-001"},
        json={
            "from_wallet_id": wallet_a,
            "to_wallet_id": wallet_b,
            "amount": "250.00000000",
        },
    )
    assert duplicate.status_code == 200

    balance_b_after = client.get(
        f"/api/v1/wallets/{wallet_b}/balance", headers=HEADERS
    )
    assert balance_b_after.json()["balance"] == "250.00000000"
