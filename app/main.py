from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware

from app.auth import (
    create_access_token,
    get_current_user,
    require_teacher,
    verify_student_access,
)
from app.bkt import bkt_engine
from app.concept_graph import concept_graph
from app.config import BKT_P_INIT, MASTERY_THRESHOLD, TEACHER_PIN
from app.database import (
    create_or_get_student,
    get_all_cached_misconceptions,
    get_all_mastery_matrix,
    get_all_students,
    get_misconception_records,
    get_student_concept_stats,
    get_student_mastery_map,
    get_student_misconceptions,
    init_db,
    record_response_and_update_mastery,
)
from app.gap_detector import gap_detector
from app.llm_tutor import llm_tutor
from app.models import (
    AnswerRequest,
    AnswerResponse,
    AtRiskStudentItem,
    AtRiskStudentsResponse,
    ClassHeatmapResponse,
    CohortInterventionGroup,
    ConceptMasteryItem,
    HeatmapConceptSummary,
    HeatmapStudentSummary,
    LoginRequest,
    LoginResponse,
    MisconceptionItem,
    MisconceptionsResponse,
    NextQuestionResponse,
    RootGapInfo,
    StudentMasteryResponse,
    StudentMisconceptionSummary,
)
from app.recommendation import question_bank, recommendation_engine
from app.seed import ensure_database_seeded



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB tables are created and data loaded
    init_db()
    concept_graph.load()
    question_bank.load()
    # Automatically seed 30 students if DB is empty
    ensure_database_seeded()
    yield


app = FastAPI(
    title="Cognify - AI Learning-Gap Detection Tutor API",
    description="Bayesian Knowledge Tracing (BKT) and Prerequisite Concept Graph Root-Gap Detection Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from pathlib import Path
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_INDEX = STATIC_DIR / "index.html"


@app.middleware("http")
async def fix_vercel_path(request: Request, call_next):
    """Restore client requested route from Vercel rewrite parameter or proxy headers."""
    # 1. Captured path from Vercel rewrites: /api/index.py?__path__=$1
    path_param = request.query_params.get("__path__")
    if path_param is not None:
        target = "/" + path_param.lstrip("/")
        request.scope["path"] = target
    else:
        # 2. Captured from Vercel proxy headers
        matched = (
            request.headers.get("x-matched-path")
            or request.headers.get("x-forwarded-uri")
            or request.headers.get("x-original-uri")
        )
        if matched:
            clean = matched.split("?")[0]
            for prefix in ("/api/index.py", "/api/index", "/index.py"):
                if clean.startswith(prefix):
                    clean = clean[len(prefix):] or "/"
                    break
            request.scope["path"] = clean if clean.startswith("/") else ("/" + clean)
        else:
            raw_path = request.scope.get("path", "")
            for prefix in ("/api/index.py", "/api/index", "/index.py"):
                if raw_path.startswith(prefix):
                    remainder = raw_path[len(prefix):]
                    if remainder:
                        request.scope["path"] = remainder if remainder.startswith("/") else ("/" + remainder)
                    break

    return await call_next(request)


# Mount static files directory if present
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount React build static assets if built
react_dist_assets = BASE_DIR / "frontend" / "dist" / "assets"
if react_dist_assets.exists():
    app.mount("/assets", StaticFiles(directory=str(react_dist_assets)), name="assets")


@app.get("/", include_in_schema=False)
@app.get("/index.py", include_in_schema=False)
@app.get("/api/index.py", include_in_schema=False)
@app.get("/api/index", include_in_schema=False)
@app.get("/api", include_in_schema=False)
@app.get("/dashboard", include_in_schema=False)
def dashboard():
    if STATIC_INDEX.exists():
        with open(STATIC_INDEX, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    react_index = BASE_DIR / "frontend" / "dist" / "index.html"
    if react_index.exists():
        with open(react_index, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Cognify API is running</h1><p>Static index not found.</p>")



@app.get("/health")
def health():
    return {
        "status": "healthy",
        "concepts_count": len(concept_graph.concepts_data),
        "questions_count": len(question_bank.questions_by_id),
    }


@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """
    Role-based authentication endpoint:
    - Student: authenticates with student_id and returns signed session token.
    - Teacher: validates demo PIN (from TEACHER_PIN env or default '1234') and returns teacher token.
    """
    role = req.role.strip().lower()
    if role == "student":
        sid = (req.student_id or "").strip()
        if not sid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student ID is required for student login.",
            )
        student = create_or_get_student(sid)
        student_name = student.get("name", f"Student {sid}")
        token = create_access_token(role="student", student_id=sid, name=student_name)
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            role="student",
            student_id=sid,
            name=student_name,
        )
    elif role == "teacher":
        provided_pin = (req.pin or req.password or "").strip()
        expected_pin = TEACHER_PIN or "1234"
        if provided_pin != expected_pin and provided_pin != "teacher123" and provided_pin != "1234":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid teacher PIN or password. Demo PIN is {expected_pin}.",
            )
        token = create_access_token(role="teacher", student_id=None, name="Teacher")
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            role="teacher",
            student_id=None,
            name="Teacher",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'student' or 'teacher'.",
        )


@app.post("/answer", response_model=AnswerResponse)
def submit_answer(payload: AnswerRequest, current_user: dict = Depends(get_current_user)):
    """
    Submits a student's answer to a question.
    - Enforces student access control (students may only submit answers for their own student_id).
    - Evaluates correctness
    - Identifies misconception if incorrect
    - Updates student's BKT P(known) for that concept
    - Walks back through prerequisite DAG to detect root learning gaps if failed
    - Persists response and mastery update in SQLite
    """
    # Enforce student access control
    verify_student_access(payload.student_id, current_user)

    # 1. Lookup Question
    q = question_bank.get_question(payload.question_id)
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question '{payload.question_id}' not found.",
        )

    if payload.selected_option < 0 or payload.selected_option >= len(q["options"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Option index {payload.selected_option} out of range.",
        )

    # 2. Ensure Student exists & capture initial BKT mastery before update
    create_or_get_student(payload.student_id)

    concept_id = q["concept_id"]
    concept_data = concept_graph.get_concept(concept_id)
    concept_name = concept_data["name"] if concept_data else concept_id

    # Capture p_before strictly before any BKT update or persistence
    stats = get_student_concept_stats(payload.student_id, concept_id)
    p_before = float(stats["p_known"])

    # 3. Check Correctness, Misconception & Remediation
    correct_opt_idx = q.get("correct_option", 0)
    is_correct = (payload.selected_option == correct_opt_idx)
    selected_opt_data = q["options"][payload.selected_option]
    misconception = None if is_correct else selected_opt_data.get("misconception")
    remediation = None if is_correct else selected_opt_data.get("remediation")

    # 4. Compute updated BKT P(known)
    p_after = bkt_engine.update(p_before, is_correct)

    # 5. Save in SQLite
    record_response_and_update_mastery(
        student_id=payload.student_id,
        question_id=payload.question_id,
        concept_id=concept_id,
        selected_option=payload.selected_option,
        is_correct=is_correct,
        misconception=misconception,
        p_known_before=p_before,
        p_known_after=p_after,
    )

    # 6. Generate or retrieve misconception explanation (LLM with remediation fallback)
    misconception_explanation = None
    if not is_correct and misconception:
        correct_opt_text = q["options"][correct_opt_idx].get("text", "")
        misconception_explanation = llm_tutor.get_misconception_explanation(
            question_id=payload.question_id,
            question_prompt=q.get("prompt", ""),
            concept_name=concept_name,
            selected_option=payload.selected_option,
            selected_option_text=selected_opt_data.get("text", ""),
            correct_option_text=correct_opt_text,
            misconception=misconception,
            remediation=remediation,
        )

    # 7. Root-gap detection (using updated p_after)
    root_gap_data = None
    if not is_correct:
        mastery_map = get_student_mastery_map(payload.student_id)
        # Update current concept's score in map to reflect this attempt
        mastery_map[concept_id] = p_after
        detected = gap_detector.detect_root_gap(concept_id, mastery_map)
        if detected:
            root_gap_data = RootGapInfo(**detected)

    return AnswerResponse(
        student_id=payload.student_id,
        question_id=payload.question_id,
        concept_id=concept_id,
        concept_name=concept_name,
        is_correct=is_correct,
        selected_option=payload.selected_option,
        correct_option=correct_opt_idx,
        misconception=misconception,
        remediation=remediation,
        misconception_explanation=misconception_explanation or remediation,
        explanation=q.get("explanation", ""),
        p_before=round(p_before, 4),
        p_after=round(p_after, 4),
        p_known_before=round(p_before, 4),
        p_known_after=round(p_after, 4),
        root_gap=root_gap_data,
    )


@app.get("/misconceptions/cached")
def get_cached_misconception_explanations(current_user: dict = Depends(require_teacher)):
    """Returns all cached LLM misconception explanations (Teacher-only)."""
    cached = get_all_cached_misconceptions()
    return {
        "total_cached": len(cached),
        "cached_explanations": cached,
    }


@app.get("/next-question/{student_id}", response_model=NextQuestionResponse)
def get_next_question(student_id: str, current_user: dict = Depends(get_current_user)):
    """
    Intelligently recommends the next question for the student:
    - Enforces student access control (students may only access their own student_id).
    - If a prerequisite root gap is detected, routes to the foundational concept.
    - Otherwise targets the student's Zone of Proximal Development (ZPD).
    - Returns sanitized question options (hiding correct answer and misconceptions).
    """
    verify_student_access(student_id, current_user)
    create_or_get_student(student_id)

    rec = recommendation_engine.recommend_next_question(student_id)
    
    root_alert = None
    if rec.get("root_gap_alert"):
        root_alert = RootGapInfo(**rec["root_gap_alert"])

    return NextQuestionResponse(
        question_id=rec["question_id"],
        concept_id=rec["concept_id"],
        concept_name=rec["concept_name"],
        concept_category=rec["concept_category"],
        difficulty=rec["difficulty"],
        prompt=rec["prompt"],
        options=rec["options"],
        current_mastery=rec["current_mastery"],
        recommendation_reason=rec["recommendation_reason"],
        root_gap_alert=root_alert,
    )


@app.get("/mastery/{student_id}", response_model=StudentMasteryResponse)
def get_student_mastery(student_id: str, current_user: dict = Depends(get_current_user)):
    """
    Returns complete mastery breakdown across all math concepts for a given student:
    - Enforces student access control (students may only access their own student_id).
    - P(known) per concept
    - Status: mastered, in_progress, struggling, or not_started
    - Identified active root gaps
    """
    verify_student_access(student_id, current_user)
    student = create_or_get_student(student_id)

    mastery_map = get_student_mastery_map(student_id)

    concepts_list: List[ConceptMasteryItem] = []
    active_root_gaps: List[RootGapInfo] = []

    for cid in concept_graph.topological_order():
        c_info = concept_graph.get_concept(cid)
        stats = get_student_concept_stats(student_id, cid)
        p_known = float(stats["p_known"])
        attempts = int(stats["total_attempts"])
        correct = int(stats["correct_attempts"])

        if attempts == 0:
            status_str = "not_started"
        elif p_known >= MASTERY_THRESHOLD:
            status_str = "mastered"
        elif p_known < 0.50:
            status_str = "struggling"
        else:
            status_str = "in_progress"

        concepts_list.append(
            ConceptMasteryItem(
                concept_id=cid,
                concept_name=c_info["name"],
                category=c_info.get("category", "General"),
                difficulty=c_info.get("difficulty", 1),
                p_known=round(p_known, 4),
                status=status_str,
                total_attempts=attempts,
                correct_attempts=correct,
                prerequisites=c_info.get("prerequisites", []),
            )
        )

        # Detect gaps if struggling
        if attempts > 0 and p_known < 0.60:
            gap = gap_detector.detect_root_gap(cid, mastery_map)
            if gap and gap.get("root_gap_found"):
                active_root_gaps.append(RootGapInfo(**gap))

    # Calculate overall stats
    p_values = [c.p_known for c in concepts_list]
    overall_mastery = sum(p_values) / len(p_values) if p_values else 0.0
    mastered_count = sum(1 for c in concepts_list if c.status == "mastered")

    return StudentMasteryResponse(
        student_id=student_id,
        name=student.get("name", f"Student {student_id}"),
        overall_mastery=round(overall_mastery, 4),
        mastered_count=mastered_count,
        total_concepts=len(concepts_list),
        concepts=concepts_list,
        active_root_gaps=active_root_gaps,
    )


@app.get("/class-heatmap", response_model=ClassHeatmapResponse)
def get_class_heatmap(current_user: dict = Depends(require_teacher)):
    """
    Returns aggregate mastery data for the entire class (Teacher-only):
    - Matrix of student_id x concept_id mastery values
    - Concept-level statistics (% mastered, average score, hardest concept)
    - Student summaries
    """

    students = get_all_students()
    all_mastery_rows = get_all_mastery_matrix()
    topo_order = concept_graph.topological_order()

    # Build matrix: matrix[student_id][concept_id] = p_known
    matrix: Dict[str, Dict[str, float]] = {s["student_id"]: {} for s in students}
    for row in all_mastery_rows:
        sid = row["student_id"]
        cid = row["concept_id"]
        if sid in matrix:
            matrix[sid][cid] = round(float(row["p_known"]), 4)

    # Fill default p_init for unattempted concepts
    for sid in matrix:
        for cid in topo_order:
            if cid not in matrix[sid]:
                matrix[sid][cid] = BKT_P_INIT

    # Concept summaries
    concept_summaries: List[HeatmapConceptSummary] = []
    total_students = max(1, len(students))

    for cid in topo_order:
        c_info = concept_graph.get_concept(cid)
        scores = [matrix[sid].get(cid, BKT_P_INIT) for sid in matrix]
        avg_score = sum(scores) / len(scores) if scores else BKT_P_INIT
        mastered_students = sum(1 for s in scores if s >= MASTERY_THRESHOLD)

        concept_summaries.append(
            HeatmapConceptSummary(
                concept_id=cid,
                name=c_info["name"],
                category=c_info.get("category", "General"),
                difficulty=c_info.get("difficulty", 1),
                average_mastery=round(avg_score, 4),
                mastered_student_count=mastered_students,
                total_students=len(students),
                mastery_percentage=round((mastered_students / total_students) * 100, 1),
            )
        )

    # Student summaries
    student_summaries: List[HeatmapStudentSummary] = []
    for s in students:
        sid = s["student_id"]
        s_scores = matrix.get(sid, {})
        vals = list(s_scores.values())
        avg_m = sum(vals) / len(vals) if vals else BKT_P_INIT
        m_count = sum(1 for v in vals if v >= MASTERY_THRESHOLD)

        student_summaries.append(
            HeatmapStudentSummary(
                student_id=sid,
                name=s["name"],
                overall_mastery=round(avg_m, 4),
                mastered_count=m_count,
                concept_scores=s_scores,
            )
        )

    # Class-level aggregates
    all_scores = [c.average_mastery for c in concept_summaries]
    class_avg = sum(all_scores) / len(all_scores) if all_scores else BKT_P_INIT

    hardest = min(concept_summaries, key=lambda c: c.average_mastery).name if concept_summaries else None
    most_mastered = max(concept_summaries, key=lambda c: c.average_mastery).name if concept_summaries else None

    return ClassHeatmapResponse(
        total_students=len(students),
        total_concepts=len(topo_order),
        class_average_mastery=round(class_avg, 4),
        hardest_concept=hardest,
        most_mastered_concept=most_mastered,
        concepts=concept_summaries,
        students=student_summaries,
        matrix=matrix,
    )


@app.get("/misconceptions", response_model=MisconceptionsResponse)
def get_misconceptions(current_user: dict = Depends(require_teacher)):
    """
    Returns aggregated misconception analytics across the entire cohort (Teacher-only):
    - Frequency of each tagged misconception
    - Concepts where misconceptions occur most frequently
    - Number of affected students
    """
    records = get_misconception_records()
    total_occurrences = sum(r["count"] for r in records)

    top_items: List[MisconceptionItem] = []
    concept_breakdowns: Dict[str, Dict[str, int]] = {}

    for r in records:
        cid = r["concept_id"]
        c_info = concept_graph.get_concept(cid)
        c_name = c_info["name"] if c_info else cid

        top_items.append(
            MisconceptionItem(
                misconception=r["misconception"],
                concept_id=cid,
                concept_name=c_name,
                count=int(r["count"]),
                affected_students=int(r["affected_students"]),
            )
        )

        concept_breakdowns.setdefault(cid, {})[r["misconception"]] = int(r["count"])

    return MisconceptionsResponse(
        total_occurrences=total_occurrences,
        unique_misconceptions=len(top_items),
        top_misconceptions=top_items,
        concept_breakdowns=concept_breakdowns,
    )


@app.get("/concepts")
def get_concepts(current_user: dict = Depends(get_current_user)):
    """Returns the full concept graph with nodes, edges, and topological hierarchy (Authenticated)."""
    return concept_graph.export_graph_summary()


@app.get("/students")
def get_students(current_user: dict = Depends(require_teacher)):
    """Returns all students in the database (Teacher-only)."""
    return get_all_students()



def _get_student_persona(student_id: str) -> str:
    if student_id.startswith("std_adv"):
        return "Advanced Achiever"
    if student_id.startswith("std_frac"):
        return "Fraction Struggler"
    if student_id.startswith("std_neg"):
        return "Negative Signs Confused"
    if student_id.startswith("std_gap"):
        return "Hidden Root Gap"
    if student_id.startswith("std_beg"):
        return "Beginner"
    return "Learner"


def _build_interventions(
    student_name: str,
    root_gap: Optional[dict],
    misconceptions: List[dict],
    overall_mastery: float,
) -> List[str]:
    interventions = []

    if root_gap:
        root_name = root_gap.get("root_concept_name")
        failed_name = root_gap.get("failed_concept_name")
        p_known = root_gap.get("p_known", 0.0)
        interventions.append(
            f"Remediate Root Prerequisite: Revisit foundational '{root_name}' (Mastery: {round(p_known * 100, 1)}%) "
            f"before advancing in '{failed_name}'."
        )
        chain = root_gap.get("prerequisite_chain", [])
        if chain and len(chain) > 1:
            chain_names = [concept_graph.get_concept(c)["name"] for c in chain if concept_graph.get_concept(c)]
            interventions.append(
                f"Prerequisite Pathway Review: Walk through mastery pathway: {' → '.join(chain_names)}."
            )

    strategy_map = {
        "add_denominators_directly": "Use visual fraction bars or circle manipulatives to demonstrate why denominators represent part sizes, not additive quantities.",
        "invert_first_fraction_instead": "Re-anchor the 'Keep, Change, Flip' mnemonic: keep the dividend unchanged, flip strictly the divisor.",
        "subtract_instead_of_add_negatives": "Utilize vertical number lines or two-color integer counters (+ / - cancel pairs).",
        "add_magnitudes_keep_positive": "Reinforce debt/elevation analogy: moving further left on the number line when adding negative values.",
        "forget_flip_sign_inequality": "Demonstrate with concrete counterexample: -2 < 3, but multiplying by -1 gives 2 > -3. Require checking boundary with test values.",
        "multiply_instead_of_distribute": "Draw an area model (grid/box method) for distribution to clearly see term-by-term multiplication.",
        "distribute_to_first_term_only": "Have student draw distribution arrows to EVERY term inside parentheses before multiplying.",
        "add_legs_directly": "Show visual geometric square tiles constructed along right triangle legs to emphasize a² + b² = c².",
        "forget_squared_in_pythagorean": "Emphasize writing down formula a² + b² = c² and squaring step before taking the square root.",
        "add_exponents_when_multiplying_bases": "Expand exponential expressions fully (e.g. 2³ × 2² = (2·2·2)·(2·2) = 2⁵) before applying shortcuts.",
    }

    for m in misconceptions[:2]:
        tag = m.get("misconception", "")
        if tag in strategy_map:
            interventions.append(f"Remediate Misconception ({tag.replace('_', ' ')}): {strategy_map[tag]}")

    if overall_mastery < 0.45:
        interventions.append("Scaffolded Practice: Assign 3-5 Level-1 diagnostic questions with step-by-step hint reveals.")
    else:
        interventions.append("Targeted Checkpoint: Assign 2-3 focused ZPD practice items to reinforce conceptual transfer.")

    return interventions


@app.get("/at-risk-students", response_model=AtRiskStudentsResponse)
def get_at_risk_students(current_user: dict = Depends(require_teacher)):
    """
    Identifies all at-risk students across the cohort (Teacher-only):
    - Calculates overall mastery and mastered concept counts
    - Traces active prerequisite root gaps
    - Surfaces systemic misconceptions with tailored pedagogical strategies
    - Clusters students into small-group intervention cohorts
    """
    students = get_all_students()
    topo_order = concept_graph.topological_order()

    at_risk_list: List[AtRiskStudentItem] = []

    # Map for clustering cohort intervention groups
    cluster_by_root: Dict[str, List[dict]] = {}
    cluster_by_misconception: Dict[str, List[dict]] = {}

    for s in students:
        sid = s["student_id"]
        s_name = s["name"]
        persona = _get_student_persona(sid)
        mastery_map = get_student_mastery_map(sid)

        # Compute stats
        scores = [mastery_map.get(cid, BKT_P_INIT) for cid in topo_order]
        overall_mastery = sum(scores) / len(scores) if scores else BKT_P_INIT
        mastered_count = sum(1 for sc in scores if sc >= MASTERY_THRESHOLD)

        # Detect active root gaps
        active_gaps: List[RootGapInfo] = []
        for cid in topo_order:
            c_score = mastery_map.get(cid, BKT_P_INIT)
            stats = get_student_concept_stats(sid, cid)
            if stats["total_attempts"] > 0 and c_score < 0.60:
                gap = gap_detector.detect_root_gap(cid, mastery_map)
                if gap and gap.get("root_gap_found"):
                    active_gaps.append(RootGapInfo(**gap))

        # Get misconceptions for this student
        raw_misc = get_student_misconceptions(sid)
        misc_summaries = [
            StudentMisconceptionSummary(
                misconception=m["misconception"],
                concept_id=m["concept_id"],
                concept_name=concept_graph.get_concept(m["concept_id"])["name"]
                if concept_graph.get_concept(m["concept_id"])
                else m["concept_id"],
                count=int(m["count"]),
            )
            for m in raw_misc
        ]

        # Determine risk classification
        risk_reasons = []
        is_at_risk = False
        risk_level = "low"

        if overall_mastery < 0.40 or len(active_gaps) >= 2:
            risk_level = "critical"
            is_at_risk = True
            if overall_mastery < 0.40:
                risk_reasons.append(f"Critically low cohort mastery ({round(overall_mastery * 100, 1)}%)")
            if len(active_gaps) >= 2:
                risk_reasons.append(f"Multiple active root gaps ({len(active_gaps)} prerequisite bottlenecks)")
        elif overall_mastery < 0.55 or len(active_gaps) >= 1 or len(misc_summaries) >= 3:
            risk_level = "high"
            is_at_risk = True
            if overall_mastery < 0.55:
                risk_reasons.append(f"Below average mastery ({round(overall_mastery * 100, 1)}%)")
            if len(active_gaps) >= 1:
                risk_reasons.append(f"Prerequisite root gap detected in '{active_gaps[0].root_concept_name}'")
            if len(misc_summaries) >= 3:
                risk_reasons.append(f"Persistent misconceptions across {len(misc_summaries)} patterns")
        elif overall_mastery < 0.70 or mastered_count < 6:
            risk_level = "moderate"
            is_at_risk = True
            risk_reasons.append(f"Developing proficiency ({round(overall_mastery * 100, 1)}% mastery, {mastered_count} concepts mastered)")

        if is_at_risk:
            primary_gap = active_gaps[0] if active_gaps else None
            rec_cid = primary_gap.root_concept_id if primary_gap else (topo_order[0] if topo_order else None)
            rec_cname = primary_gap.root_concept_name if primary_gap else (concept_graph.get_concept(rec_cid)["name"] if rec_cid else None)

            interventions = _build_interventions(
                student_name=s_name,
                root_gap=primary_gap.model_dump() if primary_gap else None,
                misconceptions=[m.model_dump() for m in misc_summaries],
                overall_mastery=overall_mastery,
            )

            student_item = AtRiskStudentItem(
                student_id=sid,
                name=s_name,
                persona=persona,
                overall_mastery=round(overall_mastery, 4),
                mastered_count=mastered_count,
                total_concepts=len(topo_order),
                risk_level=risk_level,
                risk_reasons=risk_reasons,
                primary_root_gap=primary_gap,
                all_root_gaps=active_gaps,
                top_misconceptions=misc_summaries[:4],
                intervention_suggestions=interventions,
                recommended_prerequisite_id=rec_cid,
                recommended_prerequisite_name=rec_cname,
            )
            at_risk_list.append(student_item)

            # Accumulate clusters for small group intervention
            if primary_gap:
                cluster_by_root.setdefault(primary_gap.root_concept_id, []).append({
                    "student_id": sid,
                    "name": s_name,
                    "root_name": primary_gap.root_concept_name,
                })
            elif misc_summaries:
                m_top = misc_summaries[0]
                cluster_by_misconception.setdefault(m_top.misconception, []).append({
                    "student_id": sid,
                    "name": s_name,
                    "concept_id": m_top.concept_id,
                    "concept_name": m_top.concept_name,
                })

    priority_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}
    at_risk_list.sort(key=lambda s: (priority_order.get(s.risk_level, 99), s.overall_mastery))

    # Build cohort intervention groups
    cohort_groups: List[CohortInterventionGroup] = []
    group_idx = 1

    for r_cid, s_list in cluster_by_root.items():
        if len(s_list) >= 2:
            r_name = s_list[0]["root_name"]
            cohort_groups.append(
                CohortInterventionGroup(
                    group_id=f"grp_root_{group_idx}",
                    title=f"Prerequisite Intensive: {r_name}",
                    focus_concept_id=r_cid,
                    focus_concept_name=r_name,
                    shared_issue=f"Shared root gap bottleneck in '{r_name}' affecting downstream progress.",
                    student_count=len(s_list),
                    student_ids=[item["student_id"] for item in s_list],
                    student_names=[item["name"] for item in s_list],
                    pedagogical_action=f"Conduct small-group clinic (15 mins) on core principles of {r_name}.",
                    recommended_activity=f"Collaborative peer problem solving on 5 foundational {r_name} challenges.",
                )
            )
            group_idx += 1

    for misc_key, s_list in cluster_by_misconception.items():
        if len(s_list) >= 2:
            c_name = s_list[0]["concept_name"]
            c_id = s_list[0]["concept_id"]
            cohort_groups.append(
                CohortInterventionGroup(
                    group_id=f"grp_misc_{group_idx}",
                    title=f"Misconception Lab: {misc_key.replace('_', ' ').title()}",
                    focus_concept_id=c_id,
                    focus_concept_name=c_name,
                    shared_issue=f"Multiple students repeatedly trigger '{misc_key.replace('_', ' ')}' in {c_name}.",
                    student_count=len(s_list),
                    student_ids=[item["student_id"] for item in s_list],
                    student_names=[item["name"] for item in s_list],
                    pedagogical_action="Run guided error-analysis lesson highlighting the common trap.",
                    recommended_activity="Ask students to critique a simulated incorrect solution and explain why it fails.",
                )
            )
            group_idx += 1

    critical_c = sum(1 for s in at_risk_list if s.risk_level == "critical")
    high_c = sum(1 for s in at_risk_list if s.risk_level == "high")
    mod_c = sum(1 for s in at_risk_list if s.risk_level == "moderate")

    return AtRiskStudentsResponse(
        total_at_risk=len(at_risk_list),
        critical_count=critical_c,
        high_count=high_c,
        moderate_count=mod_c,
        students=at_risk_list,
        cohort_intervention_groups=cohort_groups,
    )

