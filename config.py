import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled

# ------------------- Load Env -------------------
load_dotenv()

# Sensitive API Key from .env
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("❌ Missing API_KEY in .env")

# ------------------- Model Config -------------------
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL_NAME = "gemini-2.0-flash"

# Disable OpenAI tracing (since we’re not using OpenAI platform key)
set_tracing_disabled(True)

# ------------------- AI Client + Model -------------------
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=client
)
