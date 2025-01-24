import pytest
from sqlalchemy import create_engine, text
from app.models import Base
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)

@pytest.fixture(scope="module")
def db_engine():

    engine = create_engine("postgresql+psycopg2://user:password@db:5432/mydatabase")

    try:
        with engine.connect() as test_conn:
            test_conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.fail(f"Не удалось подключиться к БД: {str(e)}")
    
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(autouse=True)
def cleanup_tables(db_engine):
    with db_engine.connect() as connection:
        connection.execute(text("TRUNCATE TABLE wallet_requests RESTART IDENTITY CASCADE"))
        connection.commit()

def test_address_info_writes_to_db(db_engine):
    test_address = "TBHmxE1wFJXcEJgFo1QC5fkCoERwuuu68K"
    
    #Проверка пустой таблицы 
    with db_engine.connect() as connection:
        initial_count = connection.execute(text("SELECT COUNT(*) FROM wallet_requests")).scalar()
    assert initial_count == 0, "Таблица должна быть пустой перед тестом"

    #Вызов метода
    response = client.post(f"/api/address-info/?wallet_address={test_address}")
    assert response.status_code == 200, "Запрос должен возвращать 200 OK"
    
    #Проверяем структуру ответа
    response_data = response.json()
    assert set(response_data.keys()) == {"address", "balance", "bandwidth", "energy"}, "Некорректные поля в ответе"
    
    # Проверяем запись в БД
    with db_engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM wallet_requests WHERE wallet_address = :wallet_address"),
            {"wallet_address": test_address}
        )
        db_record = result.fetchone()

    assert db_record is not None, "Запись не найдена в БД"

    assert db_record.wallet_address == test_address, "Адрес кошелька не совпадает"
    assert float(db_record.balance) == pytest.approx(response_data["balance"], abs=1e-8), "Баланс не совпадает"
    assert db_record.bandwidth == response_data["bandwidth"], "Bandwidth не совпадает"
    assert db_record.energy == response_data["energy"], "Energy не совпадает"

    assert isinstance(db_record.created_at, datetime), "Отсутствует временная метка"
    assert (datetime.utcnow() - db_record.created_at).total_seconds() < 60, "Некорректное время создания"