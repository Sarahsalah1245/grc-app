from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import auth_router, risks, swot, cobit

# بينشئ الجداول في قاعدة البيانات لو مش موجودة (كافي للتطوير - للإنتاج استخدمي Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GRC Risk Intelligence API",
    description="API لحساب المخاطر (نوعي/كمي/مونت كارلو) وربطها بمعيار COBIT 2019 مع شرح AI",
    version="1.0.0",
)

# CORS: بنسمح بس لدومين الفرونت اند المحدد في .env، مش بأي دومين (*)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(risks.router)
app.include_router(swot.router)
app.include_router(cobit.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "GRC Risk Intelligence API"}
