import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

export const api = axios.create({ baseURL: BASE_URL })

// ─── Types ───────────────────────────────────────────────────────────────────

export interface Vendor {
  id: string
  name: string
  registered_jurisdiction: string
  services_in_scope: string[]
  data_categories: string[]
  has_special_category: boolean
  has_cross_border_transfers: boolean
  intake_tier: string
  created_at: string
}

export interface Assessment {
  id: string
  reference: string
  vendor_id: string
  client_scope: string
  initiated_by: string
  trigger_type: string
  status: string
  current_step: number
  risk_tier: number | null
  created_at: string
  updated_at: string
  completed_at: string | null
}

export interface AssessmentDetail extends Assessment {
  intake_output: object | null
  specialist_outputs: object | null
  gap_analysis_output: object | null
  scoring_output: object | null
  remediation_output: object | null
  report_output: object | null
  review_notes: string | null
  review_decision: string | null
}

export interface AssessmentTriggerIn {
  vendor_name: string
  registered_jurisdiction: string
  services_in_scope: string[]
  data_categories: string[]
  has_special_category: boolean
  has_cross_border_transfers: boolean
  initiated_by: string
  trigger_type?: string
}

export interface CloakResult {
  original_length: number
  redacted_length: number
  redacted_text: string
  routing: string
  tier_confirmed: string
  warnings: string[]
}

// ─── API functions ────────────────────────────────────────────────────────────

export const assessmentsApi = {
  list: (status?: string) =>
    api.get<Assessment[]>('/assessments/', { params: status ? { status } : {} }).then(r => r.data),

  get: (id: string) =>
    api.get<AssessmentDetail>(`/assessments/${id}`).then(r => r.data),

  trigger: (body: AssessmentTriggerIn) =>
    api.post<Assessment>('/assessments/', body).then(r => r.data),

  submitReview: (id: string, decision: 'approved' | 'rejected', notes?: string) =>
    api.post<Assessment>(`/assessments/${id}/review`, { decision, notes }).then(r => r.data),
}

export const cloakApi = {
  redact: (text: string, tier: string) =>
    api.post<CloakResult>('/cloak/redact', { text, tier }).then(r => r.data),

  checkRestricted: (text: string) =>
    api.get<{ is_restricted: boolean }>('/cloak/restricted-check', { params: { text } }).then(r => r.data),
}
