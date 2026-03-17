import { render, screen } from '@testing-library/react'
import { EmptyState } from '@/components/shared/EmptyState'

describe('EmptyState', () => {
  it('renders default title and description', () => {
    render(<EmptyState />)
    expect(screen.getByText('No data found')).toBeInTheDocument()
    expect(screen.getByText('There is nothing to display here yet.')).toBeInTheDocument()
  })

  it('renders custom title and description', () => {
    render(<EmptyState title="No configs yet" description="Create your first config." />)
    expect(screen.getByText('No configs yet')).toBeInTheDocument()
    expect(screen.getByText('Create your first config.')).toBeInTheDocument()
  })

  it('renders an action element when provided', () => {
    render(
      <EmptyState
        title="Empty"
        action={<button>Create Now</button>}
      />
    )
    expect(screen.getByRole('button', { name: 'Create Now' })).toBeInTheDocument()
  })

  it('does not render action when not provided', () => {
    render(<EmptyState title="Empty" />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})
