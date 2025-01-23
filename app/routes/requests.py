from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models import WalletRequest
from ..schemas  import WalletRequest as WalletRequestSchema
from ..database import get_db

router = APIRouter(prefix="/api")

@router.get("/requests/", response_model=List[WalletRequestSchema])
def get_requests(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    requests = db.query(WalletRequest).order_by(WalletRequest.created_at.desc()).offset(skip).limit(limit).all()
    return requests