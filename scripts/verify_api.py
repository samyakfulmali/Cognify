import os
import shutil
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    # Use an isolated temporary SQLite database clone to prevent test pollution of data/tutor.db
    temp_dir = tempfile.mkdtemp(prefix="cognify_verify_db_")
    temp_db_path = Path(temp_dir) / "verify_tutor.db"

    main_db = PROJECT_ROOT / "data" / "tutor.db"
    if main_db.exists():
        shutil.copy2(main_db, temp_db_path)

    prev_db_path = os.environ.get("DB_PATH")
    os.environ["DB_PATH"] = str(temp_db_path)

    try:
        from fastapi.testclient import TestClient
        from app.auth import create_access_token
        from app.database import init_db
        from app.main import app

        init_db(temp_db_path)
        client = TestClient(app)

        teacher_token = create_access_token(role="teacher", name="Teacher")
        teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

        std_frac_token = create_access_token(role="student", student_id="std_frac_01", name="Noah Miller")
        std_frac_headers = {"Authorization": f"Bearer {std_frac_token}"}

        std_gap_token = create_access_token(role="student", student_id="std_gap_01", name="Alexander Garcia")
        std_gap_headers = {"Authorization": f"Bearer {std_gap_token}"}

        print("=== HEALTH ===")
        print(client.get("/health").json())

        print("\n=== TOP MISCONCEPTIONS (Teacher) ===")
        misc = client.get("/misconceptions", headers=teacher_headers).json()
        print(f"Total misconception occurrences: {misc['total_occurrences']}")
        print(f"Unique misconceptions: {misc['unique_misconceptions']}")
        for m in misc["top_misconceptions"][:4]:
            print(f"  • {m['misconception']} ({m['concept_name']}): {m['count']} occurrences, {m['affected_students']} students")

        print("\n=== MASTERY & ROOT GAPS: std_frac_01 (Own Student Token) ===")
        m_frac = client.get("/mastery/std_frac_01", headers=std_frac_headers).json()
        print(f"Student: {m_frac['name']} | Overall Mastery: {round(m_frac['overall_mastery'] * 100, 1)}%")
        print(f"Active Root Gaps detected: {len(m_frac['active_root_gaps'])}")
        for g in m_frac["active_root_gaps"]:
            print(f"  [GAP] {g['failed_concept_name']} is failing due to root gap in: {g['root_concept_name']} (P={g['p_known']})")

        print("\n=== NEXT QUESTION RECOMMENDATION: std_gap_01 (Own Student Token) ===")
        nq = client.get("/next-question/std_gap_01", headers=std_gap_headers).json()
        print(f"Target Concept: {nq['concept_name']}")
        print(f"Recommendation Reason: {nq['recommendation_reason']}")
        print(f"Question Prompt: {nq['prompt']}")
        print("Options:")
        for opt in nq["options"]:
            print(f"  [{opt['id']}] {opt['text']}")

        print("\n=== CLASS HEATMAP SUMMARY (Teacher) ===")
        heatmap = client.get("/class-heatmap", headers=teacher_headers).json()
        print(f"Total Students: {heatmap['total_students']}")
        print(f"Total Concepts: {heatmap['total_concepts']}")
        print(f"Class Average Mastery: {round(heatmap['class_average_mastery'] * 100, 1)}%")
        print(f"Hardest Concept: {heatmap['hardest_concept']}")
        print(f"Most Mastered Concept: {heatmap['most_mastered_concept']}")

        print("\n=== ACCESS CONTROL VERIFICATION (Student -> 403) ===")
        res_forbidden = client.get("/class-heatmap", headers=std_frac_headers)
        print(f"Student accessing /class-heatmap: HTTP {res_forbidden.status_code} ({res_forbidden.json()['detail']})")
        res_other = client.get("/mastery/std_adv_01", headers=std_frac_headers)
        print(f"Student accessing other student /mastery/std_adv_01: HTTP {res_other.status_code} ({res_other.json()['detail']})")

        print("\n=== LLM TARGETED MISCONCEPTION EXPLANATION & CACHE ===")
        demo_token = create_access_token(role="student", student_id="demo_student_llm", name="Demo Student")
        demo_headers = {"Authorization": f"Bearer {demo_token}"}
        ans_resp = client.post("/answer", headers=demo_headers, json={
            "student_id": "demo_student_llm",
            "question_id": "q_frac_add_01",
            "selected_option": 1,  # 3/10 (misconception: add_denominators_directly)
        }).json()
        print(f"Question: What is 1/5 + 2/5?")
        print(f"Selected: 3/10 (Incorrect)")
        print(f"Diagnosed Misconception: {ans_resp['misconception']}")
        print(f"Targeted AI Tutor Insight: {ans_resp.get('misconception_explanation')}")

        cached_resp = client.get("/misconceptions/cached", headers=teacher_headers).json()
        print(f"Total Cached Explanations in SQLite: {cached_resp['total_cached']}")

    finally:
        if prev_db_path is not None:
            os.environ["DB_PATH"] = prev_db_path
        else:
            os.environ.pop("DB_PATH", None)
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


if __name__ == "__main__":
    main()
