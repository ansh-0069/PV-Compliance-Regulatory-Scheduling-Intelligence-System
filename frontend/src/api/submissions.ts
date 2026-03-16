/**
 * Submissions API module.
 *
 * Provides typed functions for all submission-related endpoints.
 */

import apiClient from './client';

export interface Submission {
  id: string;
  product_id: string;
  type: 'PSUR' | 'DSUR' | 'RMP';
  cycle: string;
  data_lock_point: string;
  submission_due: string;
  status: 'Planned' | 'In-Progress' | 'Submitted' | 'Overdue';
  authority: string;
  created_at: string;
  updated_at: string;
  deadlines: Deadline[];
}

export interface Deadline {
  id: string;
  milestone: string;
  due_date: string;
  completed: boolean;
  completed_at: string | null;
}

export const submissionsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<{ items: Submission[]; total: number }>('/submissions', { params }),

  get: (id: string) =>
    apiClient.get<Submission>(`/submissions/${id}`),

  create: (data: Partial<Submission>) =>
    apiClient.post<Submission>('/submissions', data),

  update: (id: string, data: Partial<Submission>) =>
    apiClient.patch<Submission>(`/submissions/${id}`, data),

  getDeadlines: (id: string) =>
    apiClient.get<Deadline[]>(`/submissions/${id}/deadlines`),

  generateSchedule: (data: { product_id: string; type: string; num_cycles: number; authority: string }) =>
    apiClient.post<Submission[]>('/submissions/generate-schedule', data),
};
