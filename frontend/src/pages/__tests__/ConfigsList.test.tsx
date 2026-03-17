import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'

import { ConfigsList } from '@/pages/ConfigsList'
import { configsApi } from '@/api/configs'
import type { ScrapeConfigResponse } from '@/types'

vi.mock('@/api/configs')

function makeConfig(overrides: Partial<ScrapeConfigResponse> = {}): ScrapeConfigResponse {
  return {
    id: 1,
    name: 'My Config',
    base_url: 'https://example.com',
    domain: 'example.com',
    use_headless_browser: false,
    wait_for_selector: null,
    custom_headers: null,
    pagination_type: 'none',
    pagination_selector: null,
    max_pages: 1,
    item_selector: '.item',
    fields: [{ name: 'title', selector: 'h1', attribute: null, transform: null, required: true, default_value: null }],
    request_delay_ms: 0,
    concurrent_requests: 1,
    schedule_cron: null,
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

function renderConfigsList() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <ConfigsList />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('ConfigsList page', () => {
  beforeEach(() => vi.clearAllMocks())

  it('shows empty state when no configs exist', async () => {
    vi.mocked(configsApi.list).mockResolvedValue([])
    renderConfigsList()
    await waitFor(() => {
      expect(screen.getByText(/no configurations yet/i)).toBeInTheDocument()
    })
  })

  it('renders a table row for each config', async () => {
    vi.mocked(configsApi.list).mockResolvedValue([
      makeConfig({ id: 1, name: 'Alpha', base_url: 'https://alpha.io' }),
      makeConfig({ id: 2, name: 'Beta', base_url: 'https://beta.io' }),
    ])
    renderConfigsList()
    await waitFor(() => {
      expect(screen.getByText('Alpha')).toBeInTheDocument()
      expect(screen.getByText('Beta')).toBeInTheDocument()
    })
  })

  it('shows field count per config', async () => {
    vi.mocked(configsApi.list).mockResolvedValue([
      makeConfig({
        fields: [
          { name: 'title', selector: 'h1', attribute: null, transform: null, required: true, default_value: null },
          { name: 'link', selector: 'a', attribute: 'href', transform: null, required: false, default_value: null },
        ],
      }),
    ])
    renderConfigsList()
    await waitFor(() => {
      // 2 fields column value
      expect(screen.getByText('2')).toBeInTheDocument()
    })
  })

  it('shows Active badge for active config and Inactive for inactive', async () => {
    vi.mocked(configsApi.list).mockResolvedValue([
      makeConfig({ id: 1, name: 'Active Config', is_active: true }),
      makeConfig({ id: 2, name: 'Inactive Config', is_active: false }),
    ])
    renderConfigsList()
    await waitFor(() => {
      // Column header is also "Active", so use getAllByText
      const activeMatches = screen.getAllByText('Active')
      // At least 2: the column header <th> + the badge in the row
      expect(activeMatches.length).toBeGreaterThanOrEqual(2)
      expect(screen.getByText('Inactive')).toBeInTheDocument()
    })
  })

  it('shows an error alert when the API call fails', async () => {
    vi.mocked(configsApi.list).mockRejectedValue(new Error('Server error'))
    renderConfigsList()
    await waitFor(() => {
      expect(screen.getByText('Server error')).toBeInTheDocument()
    })
  })

  it('renders "New Config" button in header', async () => {
    vi.mocked(configsApi.list).mockResolvedValue([])
    renderConfigsList()
    // Multiple "New Config" buttons exist (header + empty-state action)
    const buttons = await screen.findAllByRole('link', { name: /new config/i })
    expect(buttons.length).toBeGreaterThanOrEqual(1)
  })

  it('does not show pagination for a single page of results', async () => {
    vi.mocked(configsApi.list).mockResolvedValue([makeConfig()])
    renderConfigsList()
    await waitFor(() => {
      expect(screen.queryByRole('button', { name: /previous/i })).not.toBeInTheDocument()
    })
  })
})
