import json
from pathlib import Path
from typing import Dict, List, Optional
import random

from app.config import BKT_P_INIT, MASTERY_THRESHOLD, QUESTIONS_PATH, WEAK_PREREQUISITE_THRESHOLD
from app.concept_graph import ConceptGraph, concept_graph as default_graph
from app.database import get_student_answered_question_ids, get_student_mastery_map
from app.gap_detector import RootGapDetector, gap_detector as default_gap_detector


class QuestionBank:
    """Manages loaded MCQs and provides lookup and filtering."""

    def __init__(self, questions_file: Optional[Path] = None):
        self.questions_file = questions_file or QUESTIONS_PATH
        self.questions_by_id: Dict[str, dict] = {}
        self.questions_by_concept: Dict[str, List[dict]] = {}
        self.load()

    def load(self) -> None:
        if not self.questions_file.exists():
            raise FileNotFoundError(f"Questions file not found at {self.questions_file}")

        with open(self.questions_file, "r", encoding="utf-8") as f:
            q_list = json.load(f)

        self.questions_by_id.clear()
        self.questions_by_concept.clear()

        for q in q_list:
            self.questions_by_id[q["id"]] = q
            self.questions_by_concept.setdefault(q["concept_id"], []).append(q)

    def get_question(self, question_id: str) -> Optional[dict]:
        return self.questions_by_id.get(question_id)

    def get_by_concept(self, concept_id: str) -> List[dict]:
        return self.questions_by_concept.get(concept_id, [])


# Singleton instance
question_bank = QuestionBank()


class RecommendationEngine:
    """
    Intelligent recommendation engine for selecting next pedagogical question:
    1. If a student is failing an advanced concept due to a root gap, routes them
       to the weakest prerequisite first.
    2. Otherwise, identifies the student's Zone of Proximal Development (ZPD):
       concepts whose prerequisites are mastered, but the concept itself is unmastered.
    3. Selects unseen or least-recently practiced questions.
    """

    def __init__(
        self,
        graph: Optional[ConceptGraph] = None,
        bank: Optional[QuestionBank] = None,
        detector: Optional[RootGapDetector] = None,
    ):
        self.graph = graph or default_graph
        self.bank = bank or question_bank
        self.detector = detector or default_gap_detector

    def recommend_next_question(
        self,
        student_id: str,
        concept_id: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> dict:
        mastery_map = get_student_mastery_map(student_id)
        answered_ids = get_student_answered_question_ids(student_id)
        topo_order = self.graph.topological_order()

        target_concept = None
        recommendation_reason = None
        root_gap_alert = None

        # Clean subject string
        subject_clean = (subject or "").strip().lower()
        if subject_clean in ("", "all", "all subjects", "none"):
            subject_clean = None

        # Case A: Explicit concept requested by student
        if concept_id and concept_id in self.graph.concepts:
            gap_info = self.detector.detect_root_gap(concept_id, mastery_map)
            if gap_info and gap_info["root_gap_found"] and not gap_info.get("is_foundational"):
                root_cid = gap_info["root_concept_id"]
                if mastery_map.get(root_cid, BKT_P_INIT) < MASTERY_THRESHOLD:
                    target_concept = root_cid
                    root_gap_alert = gap_info
                    c_name = self.graph.get_concept(concept_id)["name"]
                    recommendation_reason = (
                        f"Subject Focus: You selected '{c_name}', but a prerequisite root gap was detected in "
                        f"'{gap_info['root_concept_name']}'. Let's practice the prerequisite first to build mastery!"
                    )
            if not target_concept:
                target_concept = concept_id
                c_name = self.graph.get_concept(concept_id)["name"]
                recommendation_reason = f"Subject Focus: Practicing '{c_name}'."

        # Case B: Specific subject / category requested by student (e.g. 'Fractions', 'Pre-Algebra')
        elif subject_clean:
            subject_concepts = [
                cid for cid in topo_order
                if self.graph.get_concept(cid).get("category", "").lower() == subject_clean
            ]

            if subject_concepts:
                # 1. Check for prerequisite root gap within or impacting this subject
                for sc in reversed(subject_concepts):
                    gap_info = self.detector.detect_root_gap(sc, mastery_map)
                    if gap_info and gap_info["root_gap_found"] and not gap_info.get("is_foundational"):
                        root_cid = gap_info["root_concept_id"]
                        if mastery_map.get(root_cid, BKT_P_INIT) < MASTERY_THRESHOLD:
                            target_concept = root_cid
                            root_gap_alert = gap_info
                            recommendation_reason = (
                                f"Subject Focus ({subject.title()}): Remediation needed for '{gap_info['failed_concept_name']}' "
                                f"due to root gap in '{gap_info['root_concept_name']}'."
                            )
                            break

                # 2. If no gap alert, find unmastered concept in this subject
                if not target_concept:
                    unmastered = [
                        cid for cid in subject_concepts
                        if mastery_map.get(cid, BKT_P_INIT) < MASTERY_THRESHOLD
                    ]
                    if unmastered:
                        target_concept = unmastered[0]
                        c_name = self.graph.get_concept(target_concept)["name"]
                        recommendation_reason = (
                            f"Subject Focus ({subject.title()}): Advancing your mastery in '{c_name}'."
                        )
                    else:
                        # All mastered in this subject; review the lowest score
                        target_concept = min(
                            subject_concepts,
                            key=lambda c: mastery_map.get(c, BKT_P_INIT)
                        )
                        c_name = self.graph.get_concept(target_concept)["name"]
                        recommendation_reason = (
                            f"Subject Mastery Review ({subject.title()}): Reinforcing practice in '{c_name}'."
                        )

        # Case C: Adaptive default (Curriculum-wide ZPD & Root Gaps)
        if not target_concept:
            struggling_concepts = [
                cid for cid, p in mastery_map.items()
                if p < 0.60
            ]
            struggling_concepts.sort(
                key=lambda c: topo_order.index(c) if c in topo_order else 999,
                reverse=True,
            )

            for sc in struggling_concepts:
                gap_info = self.detector.detect_root_gap(sc, mastery_map)
                if gap_info and gap_info["root_gap_found"] and not gap_info.get("is_foundational"):
                    root_cid = gap_info["root_concept_id"]
                    if mastery_map.get(root_cid, BKT_P_INIT) < MASTERY_THRESHOLD:
                        target_concept = root_cid
                        root_gap_alert = gap_info
                        recommendation_reason = (
                            f"Targeted Remediation: You are struggling with '{gap_info['failed_concept_name']}' "
                            f"because of a foundational gap in '{gap_info['root_concept_name']}'. "
                            f"Let's strengthen this prerequisite first!"
                        )
                        break

        # Step 2: If no active prerequisite gap, find next concept in ZPD
        if not target_concept:
            zpd_candidates = []
            for cid in topo_order:
                p_known = mastery_map.get(cid, BKT_P_INIT)
                if p_known >= MASTERY_THRESHOLD:
                    continue  # Already mastered

                # Check if all direct prerequisites are sufficiently mastered
                prereqs = self.graph.get_direct_prerequisites(cid)
                prereqs_met = all(
                    mastery_map.get(p, BKT_P_INIT) >= WEAK_PREREQUISITE_THRESHOLD
                    for p in prereqs
                )

                if prereqs_met:
                    zpd_candidates.append((cid, p_known))

            if zpd_candidates:
                # Pick the earliest / lowest-mastery candidate
                target_concept = zpd_candidates[0][0]
                concept_name = self.graph.get_concept(target_concept)["name"]
                recommendation_reason = (
                    f"Curriculum Progression: You have mastered all prerequisites for '{concept_name}'. "
                    f"Practice this concept to advance your mastery."
                )
            else:
                # If all concepts mastered or all blocked, pick the one with lowest mastery overall
                lowest_cid = min(
                    topo_order,
                    key=lambda c: mastery_map.get(c, BKT_P_INIT)
                )
                target_concept = lowest_cid
                concept_name = self.graph.get_concept(target_concept)["name"]
                recommendation_reason = (
                    f"Review & Mastery Reinforcement: Strengthening your knowledge in '{concept_name}'."
                )

        # Step 3: Pick question from target concept
        concept_questions = self.bank.get_by_concept(target_concept)
        if not concept_questions:
            # Fallback to any question
            concept_questions = list(self.bank.questions_by_id.values())

        # Prefer questions not yet answered by student
        unanswered = [q for q in concept_questions if q["id"] not in answered_ids]
        selected_q = unanswered[0] if unanswered else random.choice(concept_questions)

        # Sanitize options: do NOT reveal correct_option or misconception to the student
        sanitized_options = [
            {"id": opt["id"], "text": opt["text"]}
            for opt in selected_q["options"]
        ]

        concept_info = self.graph.get_concept(target_concept) or {}

        return {
            "question_id": selected_q["id"],
            "concept_id": target_concept,
            "concept_name": concept_info.get("name", target_concept),
            "concept_category": concept_info.get("category", "General"),
            "difficulty": concept_info.get("difficulty", 1),
            "prompt": selected_q["prompt"],
            "options": sanitized_options,
            "current_mastery": round(mastery_map.get(target_concept, BKT_P_INIT), 4),
            "recommendation_reason": recommendation_reason,
            "root_gap_alert": root_gap_alert,
        }


# Singleton instance
recommendation_engine = RecommendationEngine()
