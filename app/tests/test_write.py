import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker

from app.database import Base, get_db
from app import models


TEST_DATABASE_URL = "postgresql+psycopg2://user:password@testdb:5432/testdb"

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    
    Base.metadata.create_all(bind=test_engine)
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()

    connection.close()
    

def test_create_wallet_request(db_session: Session):

    wallet_data = {
        "wallet_address": "TBHmxE1wFJXcEJgFo1QC5fkCoERwuuu68K",
        "balance": 100.0,
        "bandwidth": 500,
        "energy": 200
    }

    wallet_request = models.WalletRequest(**wallet_data)

    db_session.add(wallet_request)
    db_session.commit()
    db_session.refresh(wallet_request)

    saved_wallet_request = db_session.query(models.WalletRequest).filter_by(wallet_address=wallet_data["wallet_address"]).first()
    
    assert saved_wallet_request is not None
    assert saved_wallet_request.wallet_address == wallet_data["wallet_address"]
    assert saved_wallet_request.balance == wallet_data["balance"]
    assert saved_wallet_request.bandwidth == wallet_data["bandwidth"]
    assert saved_wallet_request.energy == wallet_data["energy"]