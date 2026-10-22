import uuid
import pytest
from fastapi.testclient import TestClient

from app.auth import create_access_token
from app.config import BKT_P_INIT, TEACHER_PIN
from app.database import init_db
from app.main import app


@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def teacher_headers():
    token = create_access_token(role="teacher", student_id=None, name="Teacher")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def make_student_headers():
    def _make(student_id: str, name: str = None):
        token = create_access_token(role="student", student_id=student_id, name=name or f"Student {student_id}")
        return {"Authorization": f"Bearer {token}"}
    return _make


# --- Public / Unauthenticated ---

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["concepts_count"] >= 15
    assert data["questions_count"] >= 60


def test_missing_token_returns_401(client):
    """Endpoints require Authorization header; unauthenticated requests get 401."""
    assert client.get("/mastery/std_frac_01").status_code == 401
    assert client.get("/class-heatmap").status_code == 401
    assert client.get("/students").status_code == 401
    assert client.get("/misconceptions").status_code == 401
    assert client.get("/concepts").status_code == 401


def test_login_flow(client):
    """Test POST /login for both student and teacher roles."""
    # Student login
    res_s = client.post("/login", json={"role": "student", "student_id": "std_frac_01", "password": "student123"})
    assert res_s.status_code == 200
    data_s = res_s.json()
    assert data_s["role"] == "student"
    assert data_s["student_id"] == "std_frac_01"
    assert "access_token" in data_s

    # Teacher login with correct PIN
    pin = TEACHER_PIN or "1234"
    res_t = client.post("/login", json={"role": "teacher", "pin": pin})
    assert res_t.status_code == 200
    data_t = res_t.json()
    assert data_t["role"] == "teacher"
    assert "access_token" in data_t

    # Teacher login with incorrect PIN returns 401
    res_bad = client.post("/login", json={"role": "teacher", "pin": "wrong_pin_9999"})
    assert res_bad.status_code == 401


# --- Concepts (Authenticated) ---

def test_get_concepts(client, teacher_headers):
    response = client.get("/concepts", headers=teacher_headers)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 15
    assert len(data["edges"]) >= 14


# --- Student Quiz / Answer / Mastery ---

def test_post_answer_correct(client, make_student_headers):
    student_id = f"test_student_correct_{uuid.uuid4().hex[:6]}"
    headers = make_student_headers(student_id)
    payload = {
        "student_id": student_id,
        "question_id": "q_frac_add_01",
        "selected_option": 0,  # Correct option for q_frac_add_01
    }
    response = client.post("/answer", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == student_id
    assert data["is_correct"] is True
    assert data["misconception"] is None
    assert "p_before" in data
    assert "p_after" in data
    assert data["p_after"] > data["p_before"]
    assert data["p_known_after"] > data["p_known_before"]
    assert data["root_gap"] is None


def test_post_answer_incorrect_with_misconception_and_root_gap(client, make_student_headers):
    student_id = f"test_student_gap_{uuid.uuid4().hex[:6]}"
    headers = make_student_headers(student_id)
    # Option 1 for q_frac_add_01 is "3/10" with misconception "add_denominators_directly"
    payload = {
        "student_id": student_id,
        "question_id": "q_frac_add_01",
        "selected_option": 1,
    }
    response = client.post("/answer", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is False
    assert data["misconception"] == "add_denominators_directly"
    assert data.get("remediation") is not None
    assert "denominators" in data["remediation"].lower()
    assert data.get("misconception_explanation") is not None
    assert "p_before" in data
    assert "p_after" in data
    assert data["p_before"] == 0.3
    assert data["p_after"] < data["p_before"]
    # Since common_denominators has not been mastered, a root gap should be detected
    assert data["root_gap"] is not None
    assert data["root_gap"]["root_gap_found"] is True
    assert "common_denominators" in data["root_gap"]["prerequisite_chain"]
    # YouTube video tutorial and verification links should be provided for incorrect answer
    assert data.get("video_url") is not None
    assert "youtube.com" in data["video_url"]
    assert data.get("video_title") is not None
    assert data.get("video_embed_url") is not None
    assert data.get("video_search_url") is not None
    assert "youtube.com/results" in data["video_search_url"]


def test_post_answer_confused_gcf_with_lcm_remediation(client, make_student_headers):
    student_id = f"test_student_gcf_{uuid.uuid4().hex[:6]}"
    headers = make_student_headers(student_id)
    # Option 3 for q_lcd_01 is "2" with misconception "confused_gcf_with_lcm"
    payload = {
        "student_id": student_id,
        "question_id": "q_lcd_01",
        "selected_option": 3,
    }
    response = client.post("/answer", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is False
    assert data["misconception"] == "confused_gcf_with_lcm"
    assert "You picked the GCF" in data["remediation"]
    assert data["p_before"] == 0.3
    assert round(data["p_after"], 4) == 0.2432
    assert data["p_after"] < data["p_before"]


def test_post_answer_invalid_question(client, make_student_headers):
    student_id = "std_invalid"
    headers = make_student_headers(student_id)
    payload = {
        "student_id": student_id,
        "question_id": "non_existent_q_123",
        "selected_option": 0,
    }
    response = client.post("/answer", json=payload, headers=headers)
    assert response.status_code == 404


def test_post_answer_invalid_option_index(client, make_student_headers):
    student_id = "std_invalid"
    headers = make_student_headers(student_id)
    payload = {
        "student_id": student_id,
        "question_id": "q_frac_add_01",
        "selected_option": 99,
    }
    response = client.post("/answer", json=payload, headers=headers)
    assert response.status_code == 400 or response.status_code == 422


def test_get_next_question(client, make_student_headers):
    student_id = "test_next_q_student"
    headers = make_student_headers(student_id)
    response = client.get(f"/next-question/{student_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "question_id" in data
    assert "concept_id" in data
    assert "prompt" in data
    assert "options" in data
    assert len(data["options"]) == 4
    for opt in data["options"]:
        assert "is_correct" not in opt
        assert "misconception" not in opt


def test_get_mastery(client, make_student_headers):
    student_id = "test_student_correct"
    headers = make_student_headers(student_id)
    response = client.get(f"/mastery/{student_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == student_id
    assert "overall_mastery" in data
    assert len(data["concepts"]) >= 15
    assert "active_root_gaps" in data


# --- Access Control Tests (Student Forbidden from other student and teacher data) ---

def test_student_calling_other_student_mastery_gets_403(client, make_student_headers):
    """Requirement: student token calling /mastery/<other_student_id> gets 403."""
    student_headers = make_student_headers("student_alice")
    response = client.get("/mastery/student_bob", headers=student_headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_student_calling_class_heatmap_gets_403(client, make_student_headers):
    """Requirement: student token calling /class-heatmap gets 403."""
    student_headers = make_student_headers("student_alice")
    response = client.get("/class-heatmap", headers=student_headers)
    assert response.status_code == 403
    assert "Teachers only" in response.json()["detail"] or "Access denied" in response.json()["detail"]


def test_student_calling_misconceptions_gets_403(client, make_student_headers):
    """Requirement: student token calling /misconceptions gets 403."""
    student_headers = make_student_headers("student_alice")
    response = client.get("/misconceptions", headers=student_headers)
    assert response.status_code == 403


def test_student_calling_student_list_gets_403(client, make_student_headers):
    """Requirement: The student list endpoint used by the dropdown must be teacher-only."""
    student_headers = make_student_headers("student_alice")
    response = client.get("/students", headers=student_headers)
    assert response.status_code == 403


def test_student_calling_other_student_next_question_gets_403(client, make_student_headers):
    """Requirement: student token calling /next-question/<other_student_id> gets 403."""
    student_headers = make_student_headers("student_alice")
    response = client.get("/next-question/student_bob", headers=student_headers)
    assert response.status_code == 403


def test_student_submitting_answer_for_other_student_gets_403(client, make_student_headers):
    """Requirement: student token submitting /answer for another student_id in payload gets 403."""
    student_headers = make_student_headers("student_alice")
    payload = {
        "student_id": "student_bob",
        "question_id": "q_frac_add_01",
        "selected_option": 0,
    }
    response = client.post("/answer", json=payload, headers=student_headers)
    assert response.status_code == 403


def test_teacher_can_access_any_student_and_class_wide_endpoints(client, teacher_headers):
    """Teachers have full access to any student's mastery and class-wide reports."""
    # Teacher accessing student_bob's mastery
    res_m = client.get("/mastery/std_frac_01", headers=teacher_headers)
    assert res_m.status_code == 200

    # Teacher accessing class heatmap
    res_h = client.get("/class-heatmap", headers=teacher_headers)
    assert res_h.status_code == 200
    assert res_h.json()["total_students"] >= 1

    # Teacher accessing student list
    res_s = client.get("/students", headers=teacher_headers)
    assert res_s.status_code == 200
    assert len(res_s.json()) >= 1


# --- Teacher Endpoints ---

def test_get_class_heatmap(client, teacher_headers):
    response = client.get("/class-heatmap", headers=teacher_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data
    assert "total_concepts" in data
    assert "class_average_mastery" in data
    assert "concepts" in data
    assert "students" in data
    assert "matrix" in data


def test_get_misconceptions(client, teacher_headers):
    response = client.get("/misconceptions", headers=teacher_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_occurrences" in data
    assert "unique_misconceptions" in data
    assert "top_misconceptions" in data
    assert "concept_breakdowns" in data


def test_get_at_risk_students(client, teacher_headers):
    response = client.get("/at-risk-students", headers=teacher_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_at_risk" in data
    assert "students" in data
    assert "cohort_intervention_groups" in data
    assert isinstance(data["students"], list)
    if data["students"]:
        student = data["students"][0]
        assert "student_id" in student
        assert "risk_level" in student
        assert "intervention_suggestions" in student


def test_get_cached_misconceptions(client, teacher_headers):
    response = client.get("/misconceptions/cached", headers=teacher_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_cached" in data
    assert "cached_explanations" in data
    assert isinstance(data["cached_explanations"], list)


def test_get_next_question_with_subject_filter(client, make_student_headers):
    """Student can filter next questions by subject (e.g. Fractions)."""
    student_id = "std_adv_01"
    headers = make_student_headers(student_id)
    response = client.get(f"/next-question/{student_id}?subject=Fractions", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["concept_category"] == "Fractions"


def test_get_next_question_with_concept_id_filter(client, make_student_headers):
    """Student can practice a specific concept."""
    student_id = "std_adv_01"
    headers = make_student_headers(student_id)
    response = client.get(f"/next-question/{student_id}?concept_id=negative_numbers", headers=headers)
    assert response.status_code == 200
    data = response.json()
    # Concept is either targeted or remedial prerequisite
    assert data["concept_id"] == "negative_numbers"

