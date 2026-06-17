from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# In production (especially with serverless Supabase), tuning the connection pool is critical.
# We configure pool_pre_ping=True to check connection health before using it, preventing stale connection errors.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create a local session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative Base for models
Base = declarative_base()

# Dependency to get db session per request.
# This ensures connection is closed when the request lifecycle ends.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
