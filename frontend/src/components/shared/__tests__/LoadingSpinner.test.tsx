import { render, screen } from '@testing-library/react'
import { LoadingSpinner, PageLoading } from '@/components/shared/LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders with default medium size', () => {
    render(<LoadingSpinner />)
    const spinner = screen.getByRole('status')
    expect(spinner).toBeInTheDocument()
    expect(spinner).toHaveAttribute('aria-label', 'Loading')
    expect(spinner).toHaveClass('h-8', 'w-8')
  })

  it('renders small size', () => {
    render(<LoadingSpinner size="sm" />)
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('h-4', 'w-4')
  })

  it('renders large size', () => {
    render(<LoadingSpinner size="lg" />)
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('h-12', 'w-12')
  })

  it('accepts extra className', () => {
    render(<LoadingSpinner className="my-custom-class" />)
    expect(screen.getByRole('status')).toHaveClass('my-custom-class')
  })
})

describe('PageLoading', () => {
  it('renders a loading spinner inside a centred container', () => {
    render(<PageLoading />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })
})
