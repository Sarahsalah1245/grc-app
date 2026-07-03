from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    organization_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Qualitative ----------
class QualitativeRequest(BaseModel):
    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)


# ---------- Quantitative ----------
class QuantitativeRequest(BaseModel):
    asset_value: float = Field(gt=0)
    exposure_factor: float = Field(ge=0, le=1)
    aro: float = Field(ge=0)


class RosiRequest(BaseModel):
    ale_before: float
    ale_after: float
    cost_of_control: float = Field(gt=0)


# ---------- Monte Carlo ----------
class MonteCarloRequest(BaseModel):
    freq_min: float = Field(ge=0)
    freq_most_likely: float
    freq_max: float
    mag_min: float = Field(ge=0)
    mag_most_likely: float
    mag_max: float
    iterations: int = Field(default=10000, ge=1000, le=100000)


# ---------- SWOT ----------
class SwotEntryIn(BaseModel):
    category: Literal["strength", "weakness", "opportunity", "threat"]
    description: str
    weight: int = Field(default=3, ge=1, le=5)


class SwotRequest(BaseModel):
    entries: list[SwotEntryIn]


# ---------- COBIT ----------
class CobitMapRequest(BaseModel):
    risk_description: str = Field(min_length=5)


# ---------- FMEA ----------
class FmeaRequest(BaseModel):
    severity: int = Field(ge=1, le=10)
    occurrence: int = Field(ge=1, le=10)
    detection: int = Field(ge=1, le=10)


# ---------- Bow-Tie ----------
class ControlIn(BaseModel):
    name: str
    effectiveness: int = Field(ge=1, le=5)


class ThreatIn(BaseModel):
    description: str
    preventive_controls: list[ControlIn] = []


class ConsequenceIn(BaseModel):
    description: str
    severity: int = Field(ge=1, le=5)
    mitigating_controls: list[ControlIn] = []


class BowtieRequest(BaseModel):
    top_event: str
    threats: list[ThreatIn]
    consequences: list[ConsequenceIn]


# ---------- Combined risk item (full pipeline) ----------
class FullRiskAnalysisRequest(BaseModel):
    asset_name: str
    threat_description: str
    qualitative: QualitativeRequest
    quantitative: QuantitativeRequest
    monte_carlo: Optional[MonteCarloRequest] = None
    generate_ai_explanation: bool = True
    map_to_cobit: bool = True
