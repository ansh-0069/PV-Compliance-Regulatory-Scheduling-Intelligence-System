/**
 * CAPA API module.
 */

import apiClient from './client';

export interface CAPA {
  id: string;
  submission_id: string | null;
  title: string;
  description: string;
  status: 'Open' | 'Investigation' | 'Corrective Action' | 'Verification' | 'Closed';
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  owner: string;
  target_closure: string | null;
  created_at: string;
  updated_at: string;
  actions: CAPAAction[];
}

export interface CAPAAction {
  id: string;
  action_type: 'Corrective' | 'Preventive';
  description: string;
  assignee: string;
  due_date: string;
  status: string;
  completed_at: string | null;
}

export interface CAPAHistory {
  id: string;
  from_status: string;
  to_status: string;
  changed_by: string;
  comment: string | null;
  changed_at: string;
}

export const capasApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<{ items: CAPA[]; total: number }>('/capas', { params }),

  create: (data: Partial<CAPA>) =>
    apiClient.post<CAPA>('/capas', data),

  transition: (id: string, data: { to_status: string; changed_by: string; comment?: string }) =>
    apiClient.patch<CAPA>(`/capas/${id}/transition`, data),

  getHistory: (id: string) =>
    apiClient.get<CAPAHistory[]>(`/capas/${id}/history`),

  addAction: (id: string, data: Partial<CAPAAction>) =>
    apiClient.post<CAPAAction>(`/capas/${id}/actions`, data),
};
