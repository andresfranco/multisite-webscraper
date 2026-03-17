import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'

import { JobsList } from '@/pages/JobsList'
import { jobsApi } from '@/api/jobs'
import type { JobResponse } from '@/types'

vi.mock('@/api/jobs')

function makeJob(overrides: Partial<JobResponse> = {}): JobResponse {
  return {
    id: 1,
    config_id: 10,
    status: 'completed',
    started_at: '2026-01-01T00:00:00Z',
    completed_at: '2026-01-01T00:01:00Z',
    pages_scraped: 3,
    items_found: 42,
    items_created: 40,
    items_skipped: 2,
    errors: 0,
    error_message: null,
    celery_task_id: 'celery-abc',
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

function renderJobsList() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <JobsList />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('JobsList page', () => {
  beforeEach(() => vi.clearAllMocks())

  it('shows empty state when no jobs exist', async () => {
    vi.mocked(jobsApi.list).mockResolvedValue([])
    renderJobsList()
    await waitFor(() => {
      expect(screen.getByText(/no jobs have been created yet/i)).toBeInTheDocument()
    })
  })

  it('renders a table row for each job', async () => {
    vi.mocked(jobsApi.list).mockResolvedValue([
      makeJob({ id: 1, config_id: 10, status: 'completed' }),
      makeJob({ id: 2, config_id: 20, status: 'failed' }),
    ])
    renderJobsList()
    await waitFor(() => {
      expect(screen.getByText('#1')).toBeInTheDocument()
      expect(screen.getByText('#2')).toBeInTheDocument()
    })
  })

  it('renders status badges for each job', async () => {
    vi.mocked(jobsApi.list).mockResolvedValue([
      makeJob({ id: 1, status: 'running' }),
      makeJob({ id: 2, status: 'failed' }),
    ])
    renderJobsList()
    await waitFor(() => {
      expect(screen.getByText('Running')).toBeInTheDocument()
      expect(screen.getByText('Failed')).toBeInTheDocument()
    })
  })

  it('renders all status filter buttons', async () => {
    vi.mocked(jobsApi.list).mockResolvedValue([])
    renderJobsList()
    await waitFor(() => {
      for (const label of ['All', 'Pending', 'Running', 'Completed', 'Failed', 'Cancelled']) {
        expect(screen.getByRole('button', { name: label })).toBeInTheDocument()
      }
    })
  })

  it('clicking a status filter resets to page 1 and filters jobs', async () => {
    vi.mocked(jobsApi.list).mockResolvedValue([])
    renderJobsList()

    // Wait for initial render
    await waitFor(() => screen.getByRole('button', { name: 'Running' }))

    fireEvent.click(screen.getByRole('button', { name: 'Running' }))

    await waitFor(() => {
      // jobsApi.list should have been called with status: 'running'
      expect(jobsApi.list).toHaveBeenCalledWith(
        expect.objectContaining({ status: 'running' })
      )
    })
  })

  it('shows empty state with filter hint when no jobs match status filter', async () => {
    vi.mocked(jobsApi.list).mockResolvedValue([])
    renderJobsList()
    await waitFor(() => screen.getByRole('button', { name: 'Failed' }))
    fireEvent.click(screen.getByRole('button', { name: 'Failed' }))
    await waitFor(() => {
      expect(screen.getByText(/no jobs with status "failed"/i)).toBeInTheDocument()
    })
  })

  it('shows an error alert when the API call fails', async () => {
    vi.mocked(jobsApi.list).mockRejectedValue(new Error('Fetch failed'))
    renderJobsList()
    await waitFor(() => {
      expect(screen.getByText('Fetch failed')).toBeInTheDocument()
    })
  })

  it('highlights error count in red when errors > 0', async () => {
    vi.mocked(jobsApi.list).mockResolvedValue([makeJob({ errors: 5 })])
    renderJobsList()
    await waitFor(() => {
      const errorCell = screen.getByText('5')
      expect(errorCell).toHaveClass('text-red-500')
    })
  })
})
