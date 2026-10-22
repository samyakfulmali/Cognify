from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AnswerRequest(BaseModel):
    student_id: str = Field(..., description="Unique student identifier")
    question_id: str = Field(..., description="ID of question being answered")
    selected_option: int = Field(..., ge=0, le=3, description="Index of chosen option (0-3)")


class RootGapInfo(BaseModel):
    root_gap_found: bool
    is_foundational: bool
    root_concept_id: str
    root_concept_name: str
    p_known: float
    failed_concept_id: str
    failed_concept_name: str
    prerequisite_chain: List[str]
    unmastered_ancestors: List[dict]
    message: str
    video_url: Optional[str] = None
    video_title: Optional[str] = None
    video_embed_url: Optional[str] = None


class AnswerResponse(BaseModel):
    student_id: str
    question_id: str
    concept_id: str
    concept_name: str
    is_correct: bool
    selected_option: int
    correct_option: int
    misconception: Optional[str] = None
    remediation: Optional[str] = Field(
        None,
        description="Specific 1-2 sentence remediation naming the exact mistake and the correct method",
    )
    misconception_explanation: Optional[str] = Field(
        None,
        description="Targeted explanation addressing the specific cognitive misconception",
    )
    explanation: str
    p_before: float
    p_after: float
    p_known_before: float
    p_known_after: float
    root_gap: Optional[RootGapInfo] = None
    video_url: Optional[str] = Field(None, description="YouTube tutorial video URL for the concept to help solve it")
    video_title: Optional[str] = Field(None, description="Title of the recommended YouTube tutorial video")
    video_embed_url: Optional[str] = Field(None, description="Embedded YouTube player URL")
    video_channel: Optional[str] = Field(None, description="YouTube channel name (e.g. Math Antics)")
    video_search_url: Optional[str] = Field(None, description="YouTube search URL to verify the specific problem solution")


class QuestionOptionOut(BaseModel):
    id: int
    text: str


class NextQuestionResponse(BaseModel):
    question_id: str
    concept_id: str
    concept_name: str
    concept_category: str
    difficulty: int
    prompt: str
    options: List[QuestionOptionOut]
    current_mastery: float
    recommendation_reason: str
    root_gap_alert: Optional[RootGapInfo] = None


class ConceptMasteryItem(BaseModel):
    concept_id: str
    concept_name: str
    category: str
    difficulty: int
    p_known: float
    status: str  # "mastered", "in_progress", "struggling", "not_started"
    total_attempts: int
    correct_attempts: int
    prerequisites: List[str]


class StudentMasteryResponse(BaseModel):
    student_id: str
    name: str
    overall_mastery: float
    mastered_count: int
    total_concepts: int
    concepts: List[ConceptMasteryItem]
    active_root_gaps: List[RootGapInfo]


class HeatmapStudentSummary(BaseModel):
    student_id: str
    name: str
    overall_mastery: float
    mastered_count: int
    concept_scores: Dict[str, float]


class HeatmapConceptSummary(BaseModel):
    concept_id: str
    name: str
    category: str
    difficulty: int
    average_mastery: float
    mastered_student_count: int
    total_students: int
    mastery_percentage: float


class ClassHeatmapResponse(BaseModel):
    total_students: int
    total_concepts: int
    class_average_mastery: float
    hardest_concept: Optional[str] = None
    most_mastered_concept: Optional[str] = None
    concepts: List[HeatmapConceptSummary]
    students: List[HeatmapStudentSummary]
    matrix: Dict[str, Dict[str, float]]


class MisconceptionItem(BaseModel):
    misconception: str
    concept_id: str
    concept_name: str
    count: int
    affected_students: int


class MisconceptionsResponse(BaseModel):
    total_occurrences: int
    unique_misconceptions: int
    top_misconceptions: List[MisconceptionItem]
    concept_breakdowns: Dict[str, Dict[str, int]]


class StudentMisconceptionSummary(BaseModel):
    misconception: str
    concept_id: str
    concept_name: str
    count: int


class CohortInterventionGroup(BaseModel):
    group_id: str
    title: str
    focus_concept_id: str
    focus_concept_name: str
    shared_issue: str
    student_count: int
    student_ids: List[str]
    student_names: List[str]
    pedagogical_action: str
    recommended_activity: str


class AtRiskStudentItem(BaseModel):
    student_id: str
    name: str
    persona: str
    overall_mastery: float
    mastered_count: int
    total_concepts: int
    risk_level: str  # "critical", "high", "moderate"
    risk_reasons: List[str]
    primary_root_gap: Optional[RootGapInfo] = None
    all_root_gaps: List[RootGapInfo] = []
    top_misconceptions: List[StudentMisconceptionSummary] = []
    intervention_suggestions: List[str]
    recommended_prerequisite_id: Optional[str] = None
    recommended_prerequisite_name: Optional[str] = None


class AtRiskStudentsResponse(BaseModel):
    total_at_risk: int
    critical_count: int
    high_count: int
    moderate_count: int
    students: List[AtRiskStudentItem]
    cohort_intervention_groups: List[CohortInterventionGroup]


class LoginRequest(BaseModel):
    role: str = Field(..., description="'student' or 'teacher'")
    student_id: Optional[str] = Field(None, description="Student ID for student login")
    password: Optional[str] = Field(None, description="Password (demo: student123 or teacher123)")
    pin: Optional[str] = Field(None, description="Teacher PIN (default: 1234 or TEACHER_PIN)")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    student_id: Optional[str] = None
    name: Optional[str] = None


