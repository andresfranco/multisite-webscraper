import apiClient from './client'
import type {
  ScrapeConfigCreate,
  ScrapeConfigUpdate,
  ScrapeConfigResponse,
  AutoDetectRequest,
  AutoDetectResponse,
  TestConfigResponse,
  ConfigsListParams,
} from '@/types'

export const configsApi = {
  list: async (params?: ConfigsListParams): Promise<ScrapeConfigResponse[]> => {
    const { data } = await apiClient.get('/configs', { params })
    return data
  },

  get: async (id: number): Promise<ScrapeConfigResponse> => {
    const { data } = await apiClient.get(`/configs/${id}`)
    return data
  },

  create: async (payload: ScrapeConfigCreate): Promise<ScrapeConfigResponse> => {
    const { data } = await apiClient.post('/configs', payload)
    return data
  },

  update: async (id: number, payload: ScrapeConfigUpdate): Promise<ScrapeConfigResponse> => {
    const { data } = await apiClient.put(`/configs/${id}`, payload)
    return data
  },

  delete: async (id: number): Promise<{ message: string }> => {
    const { data } = await apiClient.delete(`/configs/${id}`)
    return data
  },

  autoDetect: async (payload: AutoDetectRequest): Promise<AutoDetectResponse> => {
    const { data } = await apiClient.post('/configs/auto-detect', payload)
    return data
  },

  test: async (id: number): Promise<TestConfigResponse> => {
    const { data } = await apiClient.post(`/configs/${id}/test`)
    return data
  },
}
