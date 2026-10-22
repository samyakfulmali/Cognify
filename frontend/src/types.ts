export type Theme = 'dark' | 'light';
export type UserRole = 'student' | 'teacher';

export interface Student {
  student_id: string;
  name: string;
  created_at?: string;
}

export interface QuestionOption {
  id: number;
  text: string;
}

export interface RootGapInfo {
  root_gap_found: boolean;
  is_foundational: boolean;
  root_concept_id: string;
  root_concept_name: string;
  p_known: number;
  failed_concept_id: string;
  failed_concept_name: string;
  prerequisite_chain: string[];
  unmastered_ancestors: Array<{
    concept_id: string;
    concept_name: string;
    p_known: number;
    is_weak: boolean;
  }>;
  message: string;
}

export interface NextQuestionResponse {
  question_id: string;
  concept_id: string;
  concept_name: string;
  concept_category: string;
  difficulty: number;
  prompt: string;
  options: QuestionOption[];
  current_mastery: number;
  recommendation_reason: string;
  root_gap_alert: RootGapInfo | null;
}

export interface AnswerPayload {
  student_id: string;
  question_id: string;
  selected_option: number;
}

export interface AnswerResponse {
  student_id: string;
  question_id: string;
  concept_id: string;
  concept_name: string;
  is_correct: boolean;
  selected_option: number;
  correct_option: number;
  misconception: string | null;
  remediation?: string | null;
  misconception_explanation?: string | null;
  explanation: string;
  p_before: number;
  p_after: number;
  p_known_before: number;
  p_known_after: number;
  root_gap: RootGapInfo | null;
}

export interface ConceptNode {
  id: string;
  name: string;
  category: string;
  difficulty: number;
  prerequisites: string[];
}

export interface ConceptEdge {
  source: string;
  target: string;
}

export interface ConceptGraphData {
  nodes: ConceptNode[];
  edges: ConceptEdge[];
}

export interface ConceptMasteryItem {
  concept_id: string;
  concept_name: string;
  category: string;
  difficulty: number;
  p_known: number;
  status: 'mastered' | 'in_progress' | 'struggling' | 'not_started';
  total_attempts: number;
  correct_attempts: number;
  prerequisites: string[];
}

export interface StudentMasteryResponse {
  student_id: string;
  name: string;
  overall_mastery: number;
  mastered_count: number;
  total_concepts: number;
  concepts: ConceptMasteryItem[];
  active_root_gaps: RootGapInfo[];
}

export interface HeatmapStudentSummary {
  student_id: string;
  name: string;
  overall_mastery: number;
  mastered_count: number;
  concept_scores: Record<string, number>;
}

export interface HeatmapConceptSummary {
  concept_id: string;
  name: string;
  category: string;
  difficulty: number;
  average_mastery: number;
  mastered_student_count: number;
  total_students: number;
  mastery_percentage: number;
}

export interface ClassHeatmapResponse {
  total_students: number;
  total_concepts: number;
  class_average_mastery: number;
  hardest_concept: string | null;
  most_mastered_concept: string | null;
  concepts: HeatmapConceptSummary[];
  students: HeatmapStudentSummary[];
  matrix: Record<string, Record<string, number>>;
}

export interface MisconceptionItem {
  misconception: string;
  concept_id: string;
  concept_name: string;
  count: number;
  affected_students: number;
}

export interface MisconceptionsResponse {
  total_occurrences: number;
  unique_misconceptions: number;
  top_misconceptions: MisconceptionItem[];
  concept_breakdowns: Record<string, Record<string, number>>;
}

export interface LoginPayload {
  role: 'student' | 'teacher';
  student_id?: string;
  password?: string;
  pin?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: 'student' | 'teacher';
  student_id: string | null;
  name: string | null;
}

