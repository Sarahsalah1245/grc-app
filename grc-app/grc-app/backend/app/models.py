import enum
import uuid
from datetime import datetime

from sqlalchemy import (Column, String, Float, Integer, ForeignKey,
                         DateTime, Enum, Text, JSON, Boolean)
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    admin = "admin"
    risk_manager = "risk_manager"
    auditor = "auditor"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.viewer, nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    sector = Column(String, nullable=True)  # مثلاً: بنوك، صحة، حكومي
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    risk_assessments = relationship("RiskAssessment", back_populates="organization")


class RiskAssessment(Base):
    """تقييم مخاطر واحد - ممكن يحتوي على عدة risk items."""
    __tablename__ = "risk_assessments"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(String, ForeignKey("organizations.id"))
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="risk_assessments")
    risk_items = relationship("RiskItem", back_populates="assessment", cascade="all, delete-orphan")
    swot_entries = relationship("SwotEntry", back_populates="assessment", cascade="all, delete-orphan")


class RiskItem(Base):
    """
    بند خطر واحد. بيخزن نتائج الحسابات التلاتة (qualitative / quantitative / monte carlo)
    عشان تقدري تقارني بينهم وتعرضيهم كلهم في نفس التقرير.
    """
    __tablename__ = "risk_items"

    id = Column(String, primary_key=True, default=gen_uuid)
    assessment_id = Column(String, ForeignKey("risk_assessments.id"))
    asset_name = Column(String, nullable=False)
    threat_description = Column(Text, nullable=False)
    vulnerability_description = Column(Text, nullable=True)

    # --- Qualitative ---
    likelihood_score = Column(Integer, nullable=True)   # 1-5
    impact_score = Column(Integer, nullable=True)        # 1-5
    qualitative_risk_level = Column(String, nullable=True)  # Low/Medium/High/Critical

    # --- Quantitative (FAIR / SLE-ALE style) ---
    asset_value = Column(Float, nullable=True)
    exposure_factor = Column(Float, nullable=True)     # 0-1
    sle = Column(Float, nullable=True)                 # Single Loss Expectancy
    aro = Column(Float, nullable=True)                 # Annual Rate of Occurrence
    ale = Column(Float, nullable=True)                 # Annual Loss Expectancy

    # --- Monte Carlo (نتائج مُجمّعة، التفاصيل بتتخزن في JSON) ---
    monte_carlo_result = Column(JSON, nullable=True)   # {mean, p50, p90, p95, var_95, histogram...}

    # --- COBIT mapping ---
    cobit_objectives = Column(JSON, nullable=True)      # ["APO12", "DSS05", ...]

    # --- XAI ---
    ai_explanation = Column(Text, nullable=True)        # شرح الـ LLM لنتيجة الحساب

    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship("RiskAssessment", back_populates="risk_items")


class SwotEntry(Base):
    __tablename__ = "swot_entries"

    id = Column(String, primary_key=True, default=gen_uuid)
    assessment_id = Column(String, ForeignKey("risk_assessments.id"))
    category = Column(Enum("strength", "weakness", "opportunity", "threat", name="swot_category"), nullable=False)
    description = Column(Text, nullable=False)
    weight = Column(Integer, default=3)   # 1-5 أهمية البند
    linked_risk_item_id = Column(String, ForeignKey("risk_items.id"), nullable=True)

    assessment = relationship("RiskAssessment", back_populates="swot_entries")


class AuditLog(Base):
    """سجل تدقيق - كل حاجة بتتغير في البيانات الحساسة بتتسجل هنا (متطلب أساسي في أي GRC)."""
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)      # e.g. "CREATE_RISK", "DELETE_ASSESSMENT"
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
