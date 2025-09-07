📂 Customer Support AI Agent — Project Overview
🔹 Tools & Stack

FastAPI → Build REST APIs for support system

SQLAlchemy → ORM for defining tables (Tickets, ChatHistory, Conversations)

PostgreSQL → Database for storing tickets & conversations

Uvicorn → Runs the FastAPI server (uvicorn api:app --reload)

OpenAI Agents SDK → Provides the AI support assistant logic

uv → Environment & dependency manager

📂 Folder Structure
Customer Support AI Agent/
├─ .venv/                # Virtual environment  
├─ .env                  # Secrets (DB URL, API keys)  
├─ .gitignore            # Ignore unnecessary files  
├─ .python-version       # Python version used  
├─ agent.py              # AI Agent logic (Runner + tools)  
├─ api.py                # FastAPI endpoints  
├─ config.py             # Configs (keys, DB URLs)  
├─ create_table.py       # Script to create DB tables  
├─ db.py                 # SQLAlchemy models (Tickets, Conversations, ChatHistory)  
├─ dummy_data.py         # Fake data for testing (tickets, users, chats)  
├─ pyproject.toml        # Project dependencies (uv style)  
├─ README.md             # Project description  
├─ uv.lock               # Dependency lock file  
└─ __pycache__/          # Python cache  

🔹 Database Design
1. Conversations Table

Groups chats into a thread

Links to chat_history (one-to-many)

Fields: id, customer_id

2. ChatHistory Table

Stores each user/assistant message turn

Linked to a conversation_id

Fields: id, conversation_id, customer_id, role, content

3. Tickets Table

Stores support issues raised during chat

Can be linked to conversations

Fields: id, customer_id, question, answer, category

👉 Together:

A Conversation contains many ChatHistory messages.

A Ticket is created from a user’s support question, with a stored answer.
====================================
🔹 Dummy Data

We preload dummy_data.py with test cases like:

Users → e.g., Imran Shah (ID:109)

Questions → “Do you offer student discounts?”

Answers → “Yes, we offer 20% student discount.”

Categories → “Billing”, “Technical”, “General”

👉 This helps test the agent tools before plugging in real DB queries.
================================
🔹 FastAPI Endpoints

Defined in api.py:

POST /tickets/ → Create a new support ticket

GET /tickets/{id} → Retrieve ticket by ID

GET /tickets/ → List all tickets

POST /chat/ → Save user/assistant messages in history

👉 Run with:

uvicorn api:app --reload
===========================
🔹 Learning Goals for Team

✅ Practice database modeling with SQLAlchemy
✅ Learn FastAPI endpoints for APIs
✅ Run services with Uvicorn
✅ Use Agents SDK to build an AI chatbot
✅ Understand chat memory & ticket lifecycle
✅ Move from dummy data → real DB integration

⚡ This project is small but powerful:

Builds AI Agent + DB + API in one place

Lets us practice team workflows (dummy → real)

A good step toward full customer support systems

Do you want me to also write a 1-minute pitch version (like for group presentation) so your teammates instantly get the idea?

ChatGPT can make mistakes. Check important info.