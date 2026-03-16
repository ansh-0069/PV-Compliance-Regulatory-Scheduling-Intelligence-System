/**
 * QC, Audit, and Copilot API modules.
 */

import apiClient from './client';

// ── QC ──────────────────────────────────────────────

export interface QCCheck {
  id: string;
  submission_id: string;
  file_key: string;
  status: 'Pending' | 'Running' | 'Passed' | 'Failed';
  overall_score: number | null;
  created_at: string;
  findings: QCFinding[];
}

export interface QCFinding {
  id: string;
  severity: 'Critical' | 'Major' | 'Minor' | 'Info';
  section: string;
  description: string;
  recommendation: string | null;
}

export const qcApi = {
  upload: (submissionId: string, file: File) => {
    const form = new FormData();
    form.append('submission_id', submissionId);
    form.append('file', file);
    return apiClient.post('/qc/check', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getResult: (id: string) => apiClient.get<QCCheck>(`/qc/results/${id}`),
  list: (params?: Record<string, string>) =>
    apiClient.get<{ items: QCCheck[]; total: number }>('/qc/results', { params }),
};

// ── Audit ───────────────────────────────────────────

export interface AuditScore {
  id: string;
  product_id: string | null;
  score_date: string;
  overall_score: number;
  dimension_scores: Record<string, number>;
  findings_summary: Record<string, number>;
  created_at: string;
}

export const auditApi = {
  getScore: (productId?: string) =>
    apiClient.get<AuditScore | null>('/audit/score', { params: productId ? { product_id: productId } : {} }),
  getHistory: (params?: Record<string, string>) =>
    apiClient.get<{ items: AuditScore[]; total: number }>('/audit/score/history', { params }),
  recalculate: (productId?: string) =>
    apiClient.post('/audit/score/recalculate', null, { params: productId ? { product_id: productId } : {} }),
};

// ── Copilot ──────────────────────────────────────────

export interface CopilotResponse {
  session_id: string;
  response: string;
  sources: string[];
}

export const copilotApi = {
  chat: (message: string, sessionId?: string) =>
    apiClient.post<CopilotResponse>('/copilot/chat', { message, session_id: sessionId }),
  getSession: (id: string) =>
    apiClient.get(`/copilot/sessions/${id}`),
};
