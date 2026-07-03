from fastapi import APIRouter, Depends

from app.models import User
from app.auth import get_current_user
from app.schemas import SwotRequest
from app.risk_engine.swot_engine import score_swot

router = APIRouter(prefix="/swot", tags=["SWOT Analysis"])


@router.post("/analyze")
def analyze_swot(payload: SwotRequest, user: User = Depends(get_current_user)):
    entries = [e.model_dump() for e in payload.entries]
    return score_swot(entries)
