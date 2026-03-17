import apiClient from './client'
import type { AuthUser } from '@/context/AuthContext'

// ── Request types ─────────────────────────────────────────────────────────────

export interface RegisterRequest {
  email: string
  username: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

// ── Response types ────────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: AuthUser
}

export interface ApiKeyResponse {
  api_key: string
  message: string
}

// ── API calls ─────────────────────────────────────────────────────────────────

export const authApi = {
  register: async (data: RegisterRequest): Promise<AuthUser> => {
    const res = await apiClient.post<AuthUser>('/auth/register', data)
    return res.data
  },

  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const res = await apiClient.post<TokenResponse>('/auth/login', data)
    return res.data
  },

  me: async (): Promise<AuthUser> => {
    const res = await apiClient.get<AuthUser>('/auth/me')
    return res.data
  },

  changePassword: async (data: PasswordChangeRequest): Promise<void> => {
    await apiClient.post('/auth/change-password', data)
  },

  generateApiKey: async (): Promise<ApiKeyResponse> => {
    const res = await apiClient.post<ApiKeyResponse>('/auth/api-key/generate')
    return res.data
  },

  revokeApiKey: async (): Promise<void> => {
    await apiClient.delete('/auth/api-key')
  },
}
