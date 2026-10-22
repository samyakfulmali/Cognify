import type {
  AnswerPayload,
  AnswerResponse,
  ClassHeatmapResponse,
  ConceptGraphData,
  LoginPayload,
  LoginResponse,
  MisconceptionsResponse,
  NextQuestionResponse,
  Student,
  StudentMasteryResponse,
} from '../types';

const API_BASE = ''; // Uses Vite proxy in development

export function getToken(): string | null {
  return localStorage.getItem('cognify_token');
}

export function clearAuth(): void {
  localStorage.removeItem('cognify_token');
  localStorage.removeItem('cognify_user_role');
  localStorage.removeItem('cognify_student_id');
  localStorage.removeItem('cognify_login_id');
  localStorage.removeItem('cognify_user_name');
  window.dispatchEvent(new Event('cognify_auth_change'));
}

async function authFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const token = getToken();
  const headers = new Headers(init.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  const res = await fetch(`${API_BASE}${input}`, { ...init, headers });
  if (res.status === 401 || res.status === 403) {
    clearAuth();
    throw new Error(`Authentication error (${res.status}): Please log in.`);
  }
  return res;
}

export async function loginUser(payload: LoginPayload): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Login failed.');
  }
  return res.json();
}

export async function fetchStudents(): Promise<Student[]> {
  const res = await authFetch('/students');
  if (!res.ok) throw new Error('Failed to fetch students');
  return res.json();
}

export async function fetchConcepts(): Promise<ConceptGraphData> {
  const res = await authFetch('/concepts');
  if (!res.ok) throw new Error('Failed to fetch concepts');
  return res.json();
}

export async function fetchNextQuestion(
  studentId: string,
  conceptId?: string | null,
  subject?: string | null
): Promise<NextQuestionResponse> {
  const params = new URLSearchParams();
  if (conceptId) params.set('concept_id', conceptId);
  if (subject && subject !== 'all') params.set('subject', subject);
  const query = params.toString() ? `?${params.toString()}` : '';
  const res = await authFetch(`/next-question/${encodeURIComponent(studentId)}${query}`);
  if (!res.ok) throw new Error(`Failed to fetch next question for ${studentId}`);
  return res.json();
}

export async function submitAnswer(payload: AnswerPayload): Promise<AnswerResponse> {
  const res = await authFetch('/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to submit answer');
  }
  return res.json();
}

export async function fetchStudentMastery(studentId: string): Promise<StudentMasteryResponse> {
  const res = await authFetch(`/mastery/${encodeURIComponent(studentId)}`);
  if (!res.ok) throw new Error(`Failed to fetch mastery for ${studentId}`);
  return res.json();
}

export async function fetchClassHeatmap(): Promise<ClassHeatmapResponse> {
  const res = await authFetch('/class-heatmap');
  if (!res.ok) throw new Error('Failed to fetch class heatmap');
  return res.json();
}

export async function fetchMisconceptions(): Promise<MisconceptionsResponse> {
  const res = await authFetch('/misconceptions');
  if (!res.ok) throw new Error('Failed to fetch misconceptions');
  return res.json();
}
