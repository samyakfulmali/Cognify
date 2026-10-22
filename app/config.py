import os
from pathlib import Path
from dotenv import load_dotenv

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONCEPTS_PATH = DATA_DIR / "concepts.json"
QUESTIONS_PATH = DATA_DIR / "questions.json"
# Load environment variables from .env file (if present)
load_dotenv(BASE_DIR / ".env", override=False)


def get_database_path() -> Path:
    """Returns the database path, checking DB_PATH env variable first, then VERCEL serverless tmp path."""
    env_db = os.getenv("DB_PATH", "").strip()
    if env_db:
        return Path(env_db)
    if os.getenv("VERCEL"):
        return Path("/tmp/cognify.db")
    return DATA_DIR / "tutor.db"


DATABASE_PATH = get_database_path()


# Auth Configuration
TEACHER_PIN = os.getenv("TEACHER_PIN", "1234").strip()
SECRET_KEY = os.getenv("SECRET_KEY", "cognify-secret-key-super-secure-token-signing-2026").strip()

# LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").strip()


# BKT Parameters (as specified)
# P(L0): Initial knowledge probability
BKT_P_INIT = 0.3
# P(T): Transition/learning probability
BKT_P_LEARN = 0.2
# P(S): Slip probability (knows but answers wrong)
BKT_P_SLIP = 0.1
# P(G): Guess probability (doesn't know but answers right)
BKT_P_GUESS = 0.25

# Mastery & Gap Thresholds
MASTERY_THRESHOLD = 0.85
GAP_THRESHOLD = 0.60
WEAK_PREREQUISITE_THRESHOLD = 0.65
