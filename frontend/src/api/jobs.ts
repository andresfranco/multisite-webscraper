import apiClient from './client'
import type { JobCreate, JobResponse, JobsListParams } from '@/types'

export const jobsApi = {
  list: async (params?: JobsListParams): Promise<JobResponse[]> => {
    const { data } = await apiClient.get('/jobs', { params })
    return data
  },

  get: async (id: number): Promise<JobResponse> => {
    const { data } = await apiClient.get(`/jobs/${id}`)
    return data
  },

  create: async (payload: JobCreate): Promise<JobResponse> => {
    const { data } = await apiClient.post('/jobs', payload)
    return data
  },

  cancel: async (id: number): Promise<{ message: string }> => {
    const { data } = await apiClient.post(`/jobs/${id}/cancel`)
    return data
  },
}
