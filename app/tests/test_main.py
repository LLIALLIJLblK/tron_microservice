
from fastapi.testclient import TestClient
from app.main import app  # Импортируйте ваше FastAPI приложение
from pydantic import ValidationError
import pytest

client = TestClient(app)


VALID_ADDRESS = "TBHmxE1wFJXcEJgFo1QC5fkCoERwuuu68K"
INVALID_ADDRESS = "invalid_address_123"


@pytest.mark.parametrize("address", [
    "TXoRYHE3QKq8whi57HHutdo7NEfVb5YFSS",
    "TTvYrDNmfgzvzhKbN4bjtc276ktY5njLQo",
    "TBHmxE1wFJXcEJgFo1QC5fkCoERwuuu68K",
])
def test_address_success(address):
    
    response = client.post(f"/api/address-info/?wallet_address={address}")
    
    assert response.status_code == 200, "запрос выполнен 200"
      
    data = response.json()
    
    assert "address" in data
    assert "balance" in data
    assert "bandwidth" in data
    assert "energy" in data
    
    assert isinstance(data["address"], str)
    assert isinstance(data["balance"], float)
    assert isinstance(data["bandwidth"], int)
    assert isinstance(data["energy"], int)
    
    assert data["address"] == address

def test_address_invalid_format():
    response = client.post(f"/api/address-info/?wallet_address={INVALID_ADDRESS}")
    assert response.status_code == 400, "Ошибка валидации"


@pytest.mark.parametrize("address", [
    "",
    "123",
    "TBHmxE1wFJXcEJgFo1QC5fkCoERwuuu68K" * 5
])
def test_invalid_addresses(address):
    response = client.post("/api/address-info/", json={"wallet_address": address})
    assert response.status_code == 422