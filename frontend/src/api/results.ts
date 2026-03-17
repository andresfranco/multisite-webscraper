import apiClient from './client'
import type {
  ScrapedItemResponse,
  ResultsListResponse,
  ResultStats,
  ResultsListParams,
  ExportParams,
} from '@/types'

export const resultsApi = {
  list: async (params?: ResultsListParams): Promise<ResultsListResponse> => {
    const { data } = await apiClient.get('/results', { params })
    return data
  },

  get: async (id: number): Promise<ScrapedItemResponse> => {
    const { data } = await apiClient.get(`/results/${id}`)
    return data
  },

  stats: async (): Promise<ResultStats> => {
    const { data } = await apiClient.get('/results/stats')
    return data
  },

  delete: async (id: number): Promise<{ message: string }> => {
    const { data } = await apiClient.delete(`/results/${id}`)
    return data
  },

  exportUrl: (params: ExportParams): string => {
    const baseURL = `${import.meta.env.VITE_API_URL ?? ''}/api/v1`
    const searchParams = new URLSearchParams()
    searchParams.set('format', params.format)
    if (params.config_id !== undefined) searchParams.set('config_id', String(params.config_id))
    if (params.job_id !== undefined) searchParams.set('job_id', String(params.job_id))
    return `${baseURL}/results/export?${searchParams.toString()}`
  },
}
