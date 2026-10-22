import os
import shutil
import tempfile
from pathlib import Path
import pytest

from app.concept_graph import concept_graph
from app.database import init_db
from app.recommendation import question_bank
from scripts.seed_data import seed_database


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Session-level autouse fixture for pytest:
    Creates a separate temporary SQLite database for all test runs,
    seeds it with the 30 student profiles, and sets DB_PATH.
    This guarantees the main database (data/tutor.db) is never written to or polluted by tests.
    """
    temp_dir = tempfile.mkdtemp(prefix="cognify_test_db_")
    test_db_path = Path(temp_dir) / "test_tutor.db"

    prev_db_path = os.environ.get("DB_PATH")
    os.environ["DB_PATH"] = str(test_db_path)

    # Initialize schema and seed test data in the temporary database
    init_db(test_db_path)
    seed_database(test_db_path)
    concept_graph.load()
    question_bank.load()

    yield test_db_path

    # Teardown: restore previous env variable and delete temp files
    if prev_db_path is not None:
        os.environ["DB_PATH"] = prev_db_path
    else:
        os.environ.pop("DB_PATH", None)

    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass
