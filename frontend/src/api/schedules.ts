import apiClient from './client'

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ScheduleCreateRequest {
  name: string
  config_id: number
  cron_expression: string
  is_active?: boolean
}

export interface ScheduleUpdateRequest {
  name?: string
  cron_expression?: string
  is_active?: boolean
}

export interface ScheduleResponse {
  id: number
  name: string
  config_id: number
  cron_expression: string
  is_active: boolean
  last_run_at: string | null
  next_run_at: string | null
  created_at: string
  updated_at: string
}

// ── API calls ─────────────────────────────────────────────────────────────────

export const schedulesApi = {
  list: async (): Promise<ScheduleResponse[]> => {
    const res = await apiClient.get<ScheduleResponse[]>('/schedules')
    return res.data
  },

  get: async (id: number): Promise<ScheduleResponse> => {
    const res = await apiClient.get<ScheduleResponse>(`/schedules/${id}`)
    return res.data
  },

  create: async (data: ScheduleCreateRequest): Promise<ScheduleResponse> => {
    const res = await apiClient.post<ScheduleResponse>('/schedules', data)
    return res.data
  },

  update: async (id: number, data: ScheduleUpdateRequest): Promise<ScheduleResponse> => {
    const res = await apiClient.patch<ScheduleResponse>(`/schedules/${id}`, data)
    return res.data
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/schedules/${id}`)
  },

  trigger: async (id: number): Promise<{ job_id: number }> => {
    const res = await apiClient.post<{ job_id: number }>(`/schedules/${id}/trigger`)
    return res.data
  },
}
