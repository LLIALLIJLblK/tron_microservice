from datetime import datetime
from pydantic import BaseModel
from pydantic import ConfigDict

class WalletRequestBase(BaseModel):
    wallet_address: str
    balance: float
    bandwidth: int
    energy: int

    model_config = ConfigDict(from_attributes=True)

class WalletRequest(WalletRequestBase):
    id: int
    created_at: datetime

class WalletInfoResponse(BaseModel):
    address: str  
    balance: float
    bandwidth: int
    energy: int