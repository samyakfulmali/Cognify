import logging
import random
from pathlib import Path
from typing import Optional

from app.bkt import bkt_engine
from app.concept_graph import concept_graph
from app.database import get_db_connection, init_db, record_response_and_update_mastery
from app.recommendation import question_bank

logger = logging.getLogger("cognify.seed")


def seed_database(db_path: Optional[Path] = None) -> None:
    """
    Seeds the SQLite database with exactly 30 simulated students displaying realistic mastery profiles.
    Idempotent: resets responses, student_mastery, and students each time it runs.
    """
    random.seed(42)
    logger.info(f"Initializing database tables (target: {db_path or 'default'})...")
    init_db(db_path=db_path)

    conn = get_db_connection(db_path=db_path)
    with conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("DELETE FROM responses;")
        conn.execute("DELETE FROM student_mastery;")
        conn.execute("DELETE FROM students;")
        try:
            conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('responses', 'students', 'student_mastery');")
        except Exception:
            pass
    conn.close()

    concept_graph.load()
    question_bank.load()

    # 30 Students across 5 pedagogical personas
    student_personas = [
        # Group 1: Advanced Achievers (High mastery across fractions and algebra)
        {"id": "std_adv_01", "name": "Aria Chen", "persona": "advanced"},
        {"id": "std_adv_02", "name": "Ethan Wright", "persona": "advanced"},
        {"id": "std_adv_03", "name": "Maya Patel", "persona": "advanced"},
        {"id": "std_adv_04", "name": "Liam Johnson", "persona": "advanced"},
        {"id": "std_adv_05", "name": "Sophia Rodriguez", "persona": "advanced"},
        {"id": "std_adv_06", "name": "Lucas Kim", "persona": "advanced"},

        # Group 2: Fraction Strugglers (Stuck on common denominators & fraction addition)
        {"id": "std_frac_01", "name": "Noah Miller", "persona": "fraction_struggler"},
        {"id": "std_frac_02", "name": "Emma Davis", "persona": "fraction_struggler"},
        {"id": "std_frac_03", "name": "Oliver Wilson", "persona": "fraction_struggler"},
        {"id": "std_frac_04", "name": "Ava Martinez", "persona": "fraction_struggler"},
        {"id": "std_frac_05", "name": "Elijah Taylor", "persona": "fraction_struggler"},
        {"id": "std_frac_06", "name": "Isabella Anderson", "persona": "fraction_struggler"},

        # Group 3: Negative Number & Sign Confused (Stumble on negative signs & inequalities)
        {"id": "std_neg_01", "name": "James Thomas", "persona": "negative_confused"},
        {"id": "std_neg_02", "name": "Mia Jackson", "persona": "negative_confused"},
        {"id": "std_neg_03", "name": "Benjamin White", "persona": "negative_confused"},
        {"id": "std_neg_04", "name": "Harper Harris", "persona": "negative_confused"},
        {"id": "std_neg_05", "name": "William Martin", "persona": "negative_confused"},
        {"id": "std_neg_06", "name": "Evelyn Thompson", "persona": "negative_confused"},

        # Group 4: Hidden Root Gap in Pre-Algebra (Struggling with multi-step equations due to weak fraction/combining terms)
        {"id": "std_gap_01", "name": "Alexander Garcia", "persona": "hidden_root_gap"},
        {"id": "std_gap_02", "name": "Abigail Robinson", "persona": "hidden_root_gap"},
        {"id": "std_gap_03", "name": "Daniel Clark", "persona": "hidden_root_gap"},
        {"id": "std_gap_04", "name": "Emily Lewis", "persona": "hidden_root_gap"},
        {"id": "std_gap_05", "name": "Henry Lee", "persona": "hidden_root_gap"},
        {"id": "std_gap_06", "name": "Ella Walker", "persona": "hidden_root_gap"},

        # Group 5: Early Beginners (Starting from basic fractions and pre-algebra)
        {"id": "std_beg_01", "name": "Sebastian Hall", "persona": "beginner"},
        {"id": "std_beg_02", "name": "Scarlett Allen", "persona": "beginner"},
        {"id": "std_beg_03", "name": "Jack Young", "persona": "beginner"},
        {"id": "std_beg_04", "name": "Grace Hernandez", "persona": "beginner"},
        {"id": "std_beg_05", "name": "Samuel King", "persona": "beginner"},
        {"id": "std_beg_06", "name": "Chloe Wright", "persona": "beginner"},
    ]

    # Insert students into SQLite
    conn = get_db_connection(db_path=db_path)
    with conn:
        for s in student_personas:
            conn.execute(
                "INSERT INTO students (student_id, name) VALUES (?, ?)",
                (s["id"], s["name"]),
            )
    conn.close()

    # Simulation helper per student
    total_responses_seeded = 0

    for s in student_personas:
        sid = s["id"]
        persona = s["persona"]
        mastery: dict[str, float] = {}

        def simulate_answer(q, p_correct_bias: float, preferred_misconception: str = None):
            nonlocal total_responses_seeded
            cid = q["concept_id"]
            p_before = mastery.get(cid, 0.3)

            is_correct = random.random() < p_correct_bias
            if is_correct:
                chosen_opt = q["correct_option"]
                misc = None
            else:
                wrong_opts = [opt for opt in q["options"] if not opt.get("is_correct", False)]
                if preferred_misconception:
                    matched = [o for o in wrong_opts if o.get("misconception") == preferred_misconception]
                    selected = matched[0] if matched else random.choice(wrong_opts)
                else:
                    selected = random.choice(wrong_opts)
                chosen_opt = selected["id"]
                misc = selected.get("misconception")

            p_after = bkt_engine.update(p_before, is_correct)
            mastery[cid] = p_after

            record_response_and_update_mastery(
                student_id=sid,
                question_id=q["id"],
                concept_id=cid,
                selected_option=chosen_opt,
                is_correct=is_correct,
                misconception=misc,
                p_known_before=p_before,
                p_known_after=p_after,
                db_path=db_path,
            )
            total_responses_seeded += 1

        if persona == "advanced":
            for cid in concept_graph.topological_order():
                questions = question_bank.get_by_concept(cid)
                for q in questions[:3]:
                    simulate_answer(q, p_correct_bias=0.92)

        elif persona == "fraction_struggler":
            for cid in ["fractions_basics", "equivalent_fractions"]:
                for q in question_bank.get_by_concept(cid)[:3]:
                    simulate_answer(q, p_correct_bias=0.90)

            for q in question_bank.get_by_concept("common_denominators")[:4]:
                simulate_answer(q, p_correct_bias=0.15, preferred_misconception="multiplied_denominators_instead_of_lcm")

            for q in question_bank.get_by_concept("fraction_addition")[:4]:
                simulate_answer(q, p_correct_bias=0.10, preferred_misconception="add_denominators_directly")

        elif persona == "negative_confused":
            for cid in ["fractions_basics", "equivalent_fractions", "fraction_multiplication"]:
                for q in question_bank.get_by_concept(cid)[:3]:
                    simulate_answer(q, p_correct_bias=0.88)

            for q in question_bank.get_by_concept("negative_numbers")[:4]:
                simulate_answer(q, p_correct_bias=0.15, preferred_misconception="two_negatives_make_positive_in_addition")

            for q in question_bank.get_by_concept("order_of_operations")[:3]:
                simulate_answer(q, p_correct_bias=0.20, preferred_misconception="evaluated_left_to_right_without_precedence")

            for q in question_bank.get_by_concept("linear_inequalities")[:3]:
                simulate_answer(q, p_correct_bias=0.10, preferred_misconception="forgot_to_flip_inequality_sign")

        elif persona == "hidden_root_gap":
            for q in question_bank.get_by_concept("fraction_division")[:3]:
                simulate_answer(q, p_correct_bias=0.25, preferred_misconception="multiplied_without_inverting")

            for q in question_bank.get_by_concept("combining_like_terms")[:3]:
                simulate_answer(q, p_correct_bias=0.30, preferred_misconception="combined_unlike_terms_variables_and_constants")

            for q in question_bank.get_by_concept("two_step_equations")[:3]:
                simulate_answer(q, p_correct_bias=0.30, preferred_misconception="divided_before_subtracting_constant")

            for q in question_bank.get_by_concept("multi_step_equations")[:4]:
                simulate_answer(q, p_correct_bias=0.15, preferred_misconception="forgot_to_distribute_to_second_term_in_multistep")

        elif persona == "beginner":
            for cid in ["fractions_basics", "equivalent_fractions", "negative_numbers"]:
                for q in question_bank.get_by_concept(cid)[:2]:
                    simulate_answer(q, p_correct_bias=0.65)

    logger.info(f"Successfully seeded {total_responses_seeded} student attempts across {len(student_personas)} students.")

    # Verification of student count
    conn = get_db_connection(db_path=db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM students")
        actual_count = cursor.fetchone()["count"]
        assert actual_count == len(student_personas), f"Expected {len(student_personas)} students, found {actual_count}"
    finally:
        conn.close()


def ensure_database_seeded(db_path: Optional[Path] = None) -> int:
    """
    Checks if students exist in the database. If table doesn't exist or is empty,
    initializes the tables and seeds the 30 students automatically.
    Returns the student count.
    """
    init_db(db_path=db_path)
    conn = get_db_connection(db_path=db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM students")
        row = cursor.fetchone()
        count = row["count"] if row else 0
    except Exception:
        count = 0
    finally:
        conn.close()

    if count == 0:
        logger.info("Database is empty; automatically seeding 30 students...")
        seed_database(db_path=db_path)
        count = 30

    return count
