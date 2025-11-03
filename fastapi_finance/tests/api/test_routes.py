from unittest.mock import AsyncMock, patch

def test_get_transactions_route(client):
  fake_transactions = [{
    "idx": 1,
    "date": "2015-08-31T00:00:00",
    "description": "Otwarcie rachunku",
    "amount": 0,
    "currency": "PLN",
    "paymentMethod": "Uznanie",
    "account": "mBank",
    "exchangeRate": None,
    "currencies": None,
    "calcRefIdx": None,
    "transactionType": "income",
    "createdAt": "2025-11-01T16:32:36.749000",
    "updatedAt": "2025-11-01T16:32:36.749000",
    "_id": "69063624e7365e4b30c0b473"
  }]

  with patch(
    "app.api.routes.get_all_transactions",
    AsyncMock(return_value=fake_transactions)
  ):
    response = client.get("/api/transactions/")

  assert response.status_code == 200
  assert response.json() == fake_transactions