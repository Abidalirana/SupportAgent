import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from sqlalchemy.orm import Session
from db import Ticket, ChatHistory, Conversation, get_db  # ✅ updated models
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
    raise ValueError("❌ Missing GEMINI_API_KEY in .env")

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
    """Save ticket into Postgres (auto-injected DB)."""
    db = next(get_db())
    return _save_ticket(customer_id, question, answer, category, db)

@function_tool
def search_ticket(question: str) -> str:
    """Search for existing ticket in Postgres by question text."""
    db = next(get_db())
    return _search_ticket(question, db)

# ------------------- Dummy Tools -------------------
@function_tool
def search_dummy_by_status(status: str) -> str:
    """Search dummy tickets by status (confirmed, pending, resolved)."""
    results = get_tickets_by_status(status)
    if not results:
        return f"❌ No tickets found with status {status}."
    return "\n".join([
        f"{t.customer_name} (ID:{t.customer_id}): {t.question} → {t.answer} [{t.status}]"
        for t in results
    ])

@function_tool
def search_dummy_by_customer(name: str) -> str:
    """Search dummy tickets by customer name."""
    results = get_tickets_by_customer(name)
    if not results:
        return f"❌ No tickets found for {name}."
    return "\n".join([
        f"{t.customer_name} (ID:{t.customer_id}): {t.question} → {t.answer} [{t.status}]"
        for t in results
    ])

@function_tool
def search_dummy_by_customer_id(customer_id: int) -> str:
    """Search dummy tickets by customer ID (like 104)."""
    if customer_id < 100:
        customer_id = 100 + customer_id

    results = get_ticket_by_customer_id(customer_id)
    if not results:
        return f"❌ No tickets found for customer ID {customer_id}."
    return "\n".join([
        f"{t.customer_name} (ID:{t.customer_id}): {t.question} → {t.answer} [{t.status}]"
        for t in results
    ])

@function_tool
def search_dummy_by_ticket_id(ticket_id: int) -> str:
    """Search dummy tickets by ticket ID (like 4)."""
    ticket = get_ticket_by_ticket_id(ticket_id)
    if not ticket:
        return f"❌ No ticket found with ID {ticket_id}."
    return (
        f"📌 Ticket #{ticket.id} - {ticket.customer_name} (Customer ID: {ticket.customer_id})\n"
        f"Question: {ticket.question}\nAnswer: {ticket.answer}\n"
        f"Category: {ticket.category}\nStatus: {ticket.status}"
    )

# ------------------- Chat History Saver -------------------
def save_message(conversation_id: int, customer_id: int, role: str, content: str):
    """Save chat messages (user + assistant) into DB with conversation grouping."""
    db = next(get_db())
    msg = ChatHistory(
        conversation_id=conversation_id,
        customer_id=customer_id,
        role=role,
        content=content
    )
    db.add(msg)
    db.commit()
    db.close()

# ------------------- Agent -------------------
agent = Agent(
    name="SupportAgent",
    instructions="""
    You are a support agent.
    - For real tickets: use save_ticket and search_ticket (Postgres).
    - For testing: use search_dummy_by_status, search_dummy_by_customer,
      search_dummy_by_customer_id, search_dummy_by_ticket_id (dummy data).
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

# ------------------- Runner Wrapper -------------------
async def run_agent(question: str, customer_id: int = 1):
    history = [{"role": "user", "content": question}]
    result = await Runner.run(agent, history)
    return result.final_output

# ------------------- CLI Runner -------------------
if __name__ == "__main__":
    async def main():
        print("🤖 Support Agent Ready!")

        # Start a new conversation in DB
        db = next(get_db())
        conv = Conversation(customer_id=1)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
        db.close()

        while True:
            q = input("Ask your support question (or 'exit'): ").strip()
            if q.lower() in ["exit", "quit"]:
                break

            # Save user message
            save_message(conversation_id, 1, "user", q)

            # Get AI answer
            answer = await run_agent(q, customer_id=1)

            # Save assistant reply
            save_message(conversation_id, 1, "assistant", answer)

            print(f"\n🧠 Agent Answer: {answer}\n")

    asyncio.run(main())
