from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime,Float
from .database import Base

class WalletRequest(Base):
    __tablename__ = "wallet_requests"

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String)
    balance = Column(Float)  
    bandwidth = Column(Integer)
    energy = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
