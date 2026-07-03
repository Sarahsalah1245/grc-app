from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Organization, UserRole
from app.schemas import UserCreate, UserLogin, Token
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="This email is already registered")

    org = None
    if payload.organization_name:
        org = Organization(name=payload.organization_name)
        db.add(org)
        db.flush()  # عشان ناخد الـ id قبل الـ commit

    # أول مستخدم في المنظمة بيبقى admin تلقائيًا
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=UserRole.admin,
        organization_id=org.id if org else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role.value})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # قصدًا بنرجّع نفس رسالة الخطأ في الحالتين (إيميل غلط أو باسورد غلط)
    # عشان منسهّلش على أي حد يعرف إن الإيميل ده مسجل أصلاً (user enumeration attack)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been deactivated")

    token = create_access_token({"sub": user.id, "role": user.role.value})
    return Token(access_token=token)
