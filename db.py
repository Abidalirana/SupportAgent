import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# ------------------- Load Env -------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not set in .env")

# ------------------- Engine & Session -------------------
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Logs SQL queries (disable in production)
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ------------------- Base Class -------------------
Base = declarative_base()

# ------------------- Models -------------------
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)

# ------------------- Dependency -------------------
def get_db():
    """FastAPI dependency for DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
