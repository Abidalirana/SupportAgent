import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from db import Ticket, ChatHistory, Conversation, get_db
from sqlalchemy.orm import Session
from dummy_data import (
    get_tickets_by_status,
    get_tickets_by_customer,
    get_ticket_by_customer_id,
    get_ticket_by_ticket_id,
)

# ------------------- Env + Model -------------------
load_dotenv()
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL_NAME = "gemini-2.0-flash"
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY missing in .env")

set_tracing_disabled(True)
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)

# ------------------- Real DB Tools -------------------
def _save_ticket(customer_id: int, question: str, answer: str, category: str, db: Session):
    ticket = Ticket(customer_id=customer_id, question=question, answer=answer, category=category)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return f"✅ Ticket saved with ID {ticket.id}"

def _search_ticket(question: str, db: Session):
    result = db.query(Ticket).filter(Ticket.question.ilike(f"%{question}%")).first()
    if result:
        return f"📂 Found: {result.answer}"
    return "❌ No similar ticket found."

@function_tool
def save_ticket(customer_id: int, question: str, answer: str, category: str) -> str:
    """Save a new ticket in the database"""
    db = next(get_db())
    return _save_ticket(customer_id, question, answer, category, db)

@function_tool
def search_ticket(question: str) -> str:
    """Search ticket in the database by question text"""
    db = next(get_db())
    return _search_ticket(question, db)

# ------------------- Dummy Tools -------------------
@function_tool
def search_dummy_by_status(status: str) -> str:
    """Search dummy tickets by status (resolved, pending, confirmed)."""
    results = get_tickets_by_status(status)
    if not results:
        return f"❌ No tickets with status {status}."
    return "\n".join([f"{t.customer_name} (ID:{t.customer_id}): {t.question} → {t.answer} [{t.status}]" for t in results])

@function_tool
def search_dummy_by_customer(name: str) -> str:
    """Search dummy tickets by customer name (e.g., Ali Khan)."""
    results = get_tickets_by_customer(name)
    if not results:
        return f"❌ No tickets for {name}."
    return "\n".join([f"{t.customer_name} (ID:{t.customer_id}): {t.question} → {t.answer} [{t.status}]" for t in results])

@function_tool
def search_dummy_by_customer_id(customer_id: int) -> str:
    """Search dummy tickets by numeric customer ID (e.g., 101)."""
    results = get_ticket_by_customer_id(customer_id)
    if not results:
        return f"❌ No tickets for customer ID {customer_id}."
    return "\n".join([f"{t.customer_name} (ID:{t.customer_id}): {t.question} → {t.answer} [{t.status}]" for t in results])

@function_tool
def search_dummy_by_ticket_id(ticket_id: int) -> str:
    """Search dummy tickets by ticket ID (1–10)."""
    ticket = get_ticket_by_ticket_id(ticket_id)
    if not ticket:
        return f"❌ No ticket with ID {ticket_id}."
    return f"📌 Ticket #{ticket.id} - {ticket.customer_name} (CID: {ticket.customer_id}) | {ticket.question} → {ticket.answer} [{ticket.status}]"

# ------------------- Agent -------------------
agent = Agent(
    name="SupportAgent",
    instructions="""
    You are a support agent.

    🔹 For real DB queries:
        - Use `save_ticket` to save new tickets.
        - Use `search_ticket` to search stored tickets by question text.

    🔹 For dummy data testing:
        - Use `search_dummy_by_customer_id` if user gives a number like "101 user info".
        - Use `search_dummy_by_customer` if they give a name like "Ali Khan".
        - Use `search_dummy_by_ticket_id` if they say "ticket 5" or "show ticket 5".
        - Use `search_dummy_by_status` if they ask "resolved tickets" or "pending ones".
    
    Always call the correct tool instead of saying you don’t know.
    """,
    model=model,
    tools=[
        save_ticket,
        search_ticket,
        search_dummy_by_status,
        search_dummy_by_customer,
        search_dummy_by_customer_id,
        search_dummy_by_ticket_id,
    ],
)

# ------------------- Runner -------------------
async def run_agent(question: str, customer_id: int = 1):
    history = [{"role": "user", "content": question}]
    result = await Runner.run(agent, history)
    return result.final_output

# ------------------- CLI -------------------
if __name__ == "__main__":
    async def main():
        print("🤖 Support Agent Ready!")
        db = next(get_db())
        conv = Conversation(customer_id=1)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
        db.close()

        while True:
            q = input("Ask (or 'exit'): ").strip()
            if q.lower() in ["exit", "quit"]:
                break

            answer = await run_agent(q, customer_id=1)
            print(f"\n🧠 Agent: {answer}\n")

    asyncio.run(main())
