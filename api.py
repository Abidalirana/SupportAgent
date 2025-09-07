import os
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv

# ------------------- DB Setup -------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL missing in .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(50))
    created_at = Column(DateTime, default=func.now())

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- FastAPI -------------------
from agent import run_agent  # import runner wrapper

app = FastAPI(title="Customer Support AI Agent")

@app.post("/ask")
async def ask(customer_id: int, question: str, db: Session = Depends(get_db)):
    answer = await run_agent(question, customer_id, db)
    return {"customer_id": customer_id, "question": question, "answer": answer}

@app.get("/tickets")
def get_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).all()

import uvicorn

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
