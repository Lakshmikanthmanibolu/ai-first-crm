import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crm_hcp.db")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma2-9b-it")
