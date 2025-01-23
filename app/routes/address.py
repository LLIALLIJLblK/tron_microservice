from fastapi import APIRouter, HTTPException, Depends
from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.exceptions import BadAddress
from sqlalchemy.orm import Session
from ..models import WalletRequest
from ..schemas import WalletInfoResponse

from ..database import get_db
from dotenv import load_dotenv
import os

load_dotenv()



router = APIRouter(prefix="/api")

TRON_API_KEY = os.getenv("TRON_API_KEY")

@router.post("/address-info/", response_model=WalletInfoResponse)
async def get_wallet_info(wallet_address: str, db: Session = Depends(get_db)):
    try:
        client = Tron(HTTPProvider(api_key=TRON_API_KEY))
        valid_address = client.to_base58check_address(wallet_address)
    except BadAddress:
        raise HTTPException(status_code=400, detail="Invalid wallet address")

    try:
        account_info = client.get_account(valid_address)
        balance = account_info.get('balance', 0) / 1000000

        account_resource = client.get_account_resource(valid_address)
        
        free_net_remaining = account_resource.get('freeNetLimit', 0) - account_resource.get('freeNetUsed', 0)
        net_remaining = account_resource.get('NetLimit', 0) - account_resource.get('NetUsed', 0)
        bandwidth = free_net_remaining + net_remaining

        energy = account_resource.get('EnergyLimit', 0) - account_resource.get('EnergyUsed', 0)

        db_request = WalletRequest(
            wallet_address=valid_address,
            balance=balance,
            bandwidth=bandwidth,
            energy=energy
        )
        
        db.add(db_request)
        db.commit()
        db.refresh(db_request)

        return {
            "address": valid_address,
            "balance": balance,
            "bandwidth": bandwidth,
            "energy": energy
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")