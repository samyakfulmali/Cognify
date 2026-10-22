import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.seed import ensure_database_seeded, seed_database

if __name__ == "__main__":
    seed_database()
