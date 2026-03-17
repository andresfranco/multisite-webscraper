import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'

import { Register } from '@/pages/Register'
import { authApi } from '@/api/auth'
import * as AuthContextModule from '@/context/AuthContext'

vi.mock('@/api/auth')

const mockLogin = vi.fn()
vi.spyOn(AuthContextModule, 'useAuth').mockReturnValue({
  login: mockLogin,
  logout: vi.fn(),
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
})

function renderRegister() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Register page', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders the registration form', () => {
    renderRegister()
    expect(screen.getByRole('heading', { name: /create account/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
  })

  it('shows a link to the login page', () => {
    renderRegister()
    expect(screen.getByRole('link', { name: /sign in/i })).toHaveAttribute('href', '/login')
  })

  it('calls register then login on successful submit', async () => {
    const fakeUser = {
      id: 2,
      email: 'new@example.com',
      username: 'newuser',
      is_active: true,
      is_superuser: false,
      created_at: '2026-01-01T00:00:00Z',
      last_login_at: null,
    }
    vi.mocked(authApi.register).mockResolvedValue(fakeUser)
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'abc',
      token_type: 'bearer',
      expires_in: 3600,
      user: fakeUser,
    })

    renderRegister()

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'new@example.com' } })
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'newuser' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))

    await waitFor(() => {
      expect(authApi.register).toHaveBeenCalledWith({
        email: 'new@example.com',
        username: 'newuser',
        password: 'password123',
      })
      expect(authApi.login).toHaveBeenCalledWith({
        email: 'new@example.com',
        password: 'password123',
      })
      expect(mockLogin).toHaveBeenCalledWith('abc', fakeUser)
    })
  })

  it('displays an error when registration fails', async () => {
    vi.mocked(authApi.register).mockRejectedValue(new Error('Email already registered'))

    renderRegister()

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'dup@example.com' } })
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'dupuser' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))

    await waitFor(() => {
      expect(screen.getByText('Email already registered')).toBeInTheDocument()
    })
  })
})
