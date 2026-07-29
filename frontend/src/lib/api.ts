import type { CandidateResponse, CandidateResumeDetail } from '../types/resume';

const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://localhost:8000';

export async function createCandidate(): Promise<CandidateResponse> {
  const res = await fetch(`${API_BASE}/candidates/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Failed to initialize candidate session.');
  }

  return res.json();
}

export async function uploadResume(
  candidateId: string,
  file: File
): Promise<{ id: string; candidate_id: string; filename: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/candidates/${candidateId}/resume`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    const message = typeof errorData.detail === 'string' 
      ? errorData.detail 
      : JSON.stringify(errorData.detail || 'PDF Upload failed');
    throw new Error(message);
  }

  return res.json();
}

export async function getResumeDetail(
  candidateId: string,
  resumeId: string
): Promise<CandidateResumeDetail> {
  const res = await fetch(`${API_BASE}/candidates/${candidateId}/resume/${resumeId}`);

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Failed to fetch resume processing state.');
  }

  return res.json();
}
