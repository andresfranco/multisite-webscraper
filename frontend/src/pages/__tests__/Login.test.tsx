/**
 * Tests for the Login page component.
 *
 * Strategy: mock authApi and AuthContext so we don't hit the network.
 * React Router and React Query are provided via wrapper helpers.
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'

import { Login } from '@/pages/Login'
import { authApi } from '@/api/auth'
import * as AuthContextModule from '@/context/AuthContext'

// ── Mocks ─────────────────────────────────────────────────────────────────────

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

// ── Helper ────────────────────────────────────────────────────────────────────

function renderLogin(initialPath = '/login') {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[initialPath]}>
        <Login />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe('Login page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the sign-in form', () => {
    renderLogin()
    expect(screen.getByRole('heading', { name: /sign in/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('shows a link to the register page', () => {
    renderLogin()
    expect(screen.getByRole('link', { name: /register/i })).toHaveAttribute('href', '/register')
  })

  it('calls authApi.login and AuthContext.login on successful submit', async () => {
    const fakeUser = {
      id: 1,
      email: 'user@example.com',
      username: 'user',
      is_active: true,
      is_superuser: false,
      created_at: '2026-01-01T00:00:00Z',
      last_login_at: null,
    }
    vi.mocked(authApi.login).mockResolvedValue({ access_token: 'tok123', user: fakeUser })

    renderLogin()

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'user@example.com' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'secret123' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith({ email: 'user@example.com', password: 'secret123' })
      expect(mockLogin).toHaveBeenCalledWith('tok123', fakeUser)
    })
  })

  it('displays an error alert when login fails', async () => {
    vi.mocked(authApi.login).mockRejectedValue(new Error('Invalid credentials'))

    renderLogin()

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'bad@example.com' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrongpass' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
    })
  })

  it('disables the button while loading', async () => {
    // Never resolves — keeps the component in "loading" state
    vi.mocked(authApi.login).mockReturnValue(new Promise(() => {}))

    renderLogin()

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'u@example.com' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass1234' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /signing in/i })).toBeDisabled()
    })
  })
})
