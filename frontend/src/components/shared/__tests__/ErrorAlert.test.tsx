import { render, screen } from '@testing-library/react'
import { ErrorAlert } from '@/components/shared/ErrorAlert'

describe('ErrorAlert', () => {
  it('renders default title and message', () => {
    render(<ErrorAlert message="Something went wrong" />)
    expect(screen.getByText('Error')).toBeInTheDocument()
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('renders a custom title', () => {
    render(<ErrorAlert title="Network Error" message="Could not connect" />)
    expect(screen.getByText('Network Error')).toBeInTheDocument()
    expect(screen.getByText('Could not connect')).toBeInTheDocument()
  })

  it('renders the alert role', () => {
    render(<ErrorAlert message="Oops" />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })
})
