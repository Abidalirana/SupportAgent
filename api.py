from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import Ticket, get_db
from agent import run_agent

app = FastAPI(title="Customer Support AI Agent")

@app.post("/ask")
async def ask(customer_id: int, question: str, db: Session = Depends(get_db)):
    """Ask a support question → AI Agent + DB"""
    answer = await run_agent(question, customer_id)
    return {"customer_id": customer_id, "question": question, "answer": answer}

@app.get("/tickets")
def get_tickets(db: Session = Depends(get_db)):
    """Return all stored tickets"""
    tickets = db.query(Ticket).all()
    return [
        {
            "id": t.id,
            "customer_id": t.customer_id,
            "question": t.question,
            "answer": t.answer,
            "category": t.category,
        }
        for t in tickets
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
