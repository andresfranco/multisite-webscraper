import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'

import { Dashboard } from '@/pages/Dashboard'
import { configsApi } from '@/api/configs'
import { jobsApi } from '@/api/jobs'
import { resultsApi } from '@/api/results'
import type { ScrapeConfigResponse, JobResponse, ResultsListResponse } from '@/types'

vi.mock('@/api/configs')
vi.mock('@/api/jobs')
vi.mock('@/api/results')

// Minimal fixtures
const noConfigs: ScrapeConfigResponse[] = []
const noJobs: JobResponse[] = []
const noResults: ResultsListResponse = { items: [], total: 0, page: 1, page_size: 1, pages: 0 }

function makeJob(overrides: Partial<JobResponse> = {}): JobResponse {
  return {
    id: 1,
    config_id: 10,
    status: 'completed',
    started_at: '2026-01-01T00:00:00Z',
    completed_at: '2026-01-01T00:01:00Z',
    pages_scraped: 2,
    items_found: 10,
    items_created: 10,
    items_skipped: 0,
    errors: 0,
    error_message: null,
    celery_task_id: null,
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

function renderDashboard() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Dashboard page', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders the Dashboard heading', async () => {
    vi.mocked(configsApi.list).mockResolvedValue(noConfigs)
    vi.mocked(jobsApi.list).mockResolvedValue(noJobs)
    vi.mocked(resultsApi.list).mockResolvedValue(noResults)

    renderDashboard()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('renders stat cards with zero counts when all APIs return empty', async () => {
    vi.mocked(configsApi.list).mockResolvedValue(noConfigs)
    vi.mocked(jobsApi.list).mockResolvedValue(noJobs)
    vi.mocked(resultsApi.list).mockResolvedValue(noResults)

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('Total Configs')).toBeInTheDocument()
      expect(screen.getByText('Total Jobs')).toBeInTheDocument()
      expect(screen.getByText('Total Results')).toBeInTheDocument()
      expect(screen.getByText('Active Jobs')).toBeInTheDocument()
    })
  })

  it('shows "No jobs yet" empty state when there are no recent jobs', async () => {
    vi.mocked(configsApi.list).mockResolvedValue(noConfigs)
    vi.mocked(jobsApi.list).mockResolvedValue(noJobs)
    vi.mocked(resultsApi.list).mockResolvedValue(noResults)

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('No jobs yet')).toBeInTheDocument()
    })
  })

  it('renders recent jobs in a table', async () => {
    vi.mocked(configsApi.list).mockResolvedValue(noConfigs)
    vi.mocked(jobsApi.list).mockResolvedValue([
      makeJob({ id: 7, status: 'running' }),
      makeJob({ id: 8, status: 'completed' }),
    ])
    vi.mocked(resultsApi.list).mockResolvedValue(noResults)

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('#7')).toBeInTheDocument()
      expect(screen.getByText('#8')).toBeInTheDocument()
      expect(screen.getByText('Running')).toBeInTheDocument()
      expect(screen.getByText('Completed')).toBeInTheDocument()
    })
  })

  it('shows an error alert when any API call fails', async () => {
    vi.mocked(configsApi.list).mockRejectedValue(new Error('API down'))
    vi.mocked(jobsApi.list).mockResolvedValue(noJobs)
    vi.mocked(resultsApi.list).mockResolvedValue(noResults)

    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('API down')).toBeInTheDocument()
    })
  })

  it('renders "New Config" and "View All Jobs" quick-action buttons', async () => {
    vi.mocked(configsApi.list).mockResolvedValue(noConfigs)
    vi.mocked(jobsApi.list).mockResolvedValue(noJobs)
    vi.mocked(resultsApi.list).mockResolvedValue(noResults)

    renderDashboard()

    await waitFor(() => {
      expect(screen.getAllByRole('link', { name: /new config/i }).length).toBeGreaterThanOrEqual(1)
      expect(screen.getByRole('link', { name: /view all jobs/i })).toBeInTheDocument()
    })
  })
})
