customer-support-agent/
├─ .env
├─ pyproject.toml
└─ src/
   └─ app/
      ├─ __init__.py
      ├─ config.py     # env + client + model setup
      ├─ db.py         # postgres connection
      ├─ models.py     # SQLAlchemy models
      ├─ tools.py      # agent tools (save/search ticket)
      ├─ api.py        # FastAPI routes + agent
      ├─ main.py       # FastAPI entry
      └─ runner.py     # CLI test runner
