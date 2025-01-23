import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app  
from app.database import Base, get_db  

# Настройка тестовой базы данных (используем PostgreSQL)
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://user:password@db:5432/mydatabase"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблиц в тестовой базе данных
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

@pytest.mark.asyncio
async def test_get_wallet_info(test_client):
    test_addresses = [
        "TBHmxE1wFJXcEJgFo1QC5fkCoERwuuu68K",
        "TMAqheVWMaNm15UJTNgasEVpJ7YHYiZVZ8",
        "TXfyYGFydbXY4dgV1FdZD7iL8Mym1eH9Ha"
    ]

    for address in test_addresses:
        response = test_client.post(f"/api/address-info/?wallet_address={address}")
        assert response.status_code == 200
        data = response.json()
        assert data["address"] == address
        assert "balance" in data
        assert "bandwidth" in data
        assert "energy" in data
        
@pytest.mark.asyncio        
async def test_get_wallet_info_invalid_address(test_client):

    invalid_address = "invalid_wallet_address"
    response = test_client.post(f"/api/address-info/?wallet_address={invalid_address}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid wallet address"

@pytest.mark.asyncio
def test_request_history(test_client):
    response = test_client.get("api/requests/?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
