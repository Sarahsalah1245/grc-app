from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# pool_pre_ping يتأكد إن الاتصال شغال قبل كل query (مهم لـ Supabase اللي بتقفل idle connections)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency بتفتح session وتقفلها تلقائي بعد كل request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
