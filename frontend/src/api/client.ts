import axios from 'axios'

const baseURL = `${import.meta.env.VITE_API_URL ?? ''}/api/v1`

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor — attach JWT from localStorage if present
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('ws_token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// Response interceptor — consistent error handling + redirect on 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear stale session and redirect to login
      localStorage.removeItem('ws_token')
      localStorage.removeItem('ws_user')
      window.location.href = '/login'
    }
    const message =
      error.response?.data?.detail ??
      error.response?.data?.message ??
      error.message ??
      'An unexpected error occurred'
    return Promise.reject(new Error(message))
  }
)

export default apiClient
