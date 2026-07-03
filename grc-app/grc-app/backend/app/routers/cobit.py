import json
from pathlib import Path
from fastapi import APIRouter, Depends

from app.models import User
from app.auth import get_current_user
from app.schemas import CobitMapRequest
from app.llm.cobit_rag import map_risk_to_cobit

router = APIRouter(prefix="/cobit", tags=["COBIT Mapping"])

_DATA_PATH = Path(__file__).parent.parent / "data" / "cobit_2019.json"


@router.get("/objectives")
def list_objectives():
    """بترجع كل أهداف COBIT 2019 المتاحة في النظام (مفيدة لعرضها كمرجع في الفرونت اند)."""
    return json.loads(_DATA_PATH.read_text(encoding="utf-8"))


@router.post("/map")
def map_risk(payload: CobitMapRequest, user: User = Depends(get_current_user)):
    return map_risk_to_cobit(payload.risk_description)
