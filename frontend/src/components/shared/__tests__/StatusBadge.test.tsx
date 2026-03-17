import { render, screen } from '@testing-library/react'

import { StatusBadge } from '@/components/shared/StatusBadge'

describe('StatusBadge', () => {
  it('renders running status text', () => {
    render(<StatusBadge status="running" />)

    expect(screen.getByText(/running/i)).toBeInTheDocument()
  })

  it('renders completed status text', () => {
    render(<StatusBadge status="completed" />)

    expect(screen.getByText(/completed/i)).toBeInTheDocument()
  })
})
