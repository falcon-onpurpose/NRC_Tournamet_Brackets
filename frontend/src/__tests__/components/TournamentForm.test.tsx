import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TournamentForm from '@/components/TournamentForm'

// Mock the API client
const mockCreateTournament = jest.fn()
jest.mock('@/lib/api', () => ({
  createTournament: mockCreateTournament,
}))

// Mock Next.js router
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

describe('TournamentForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders form fields', () => {
    render(<TournamentForm />)
    
    expect(screen.getByLabelText(/Tournament Name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Start Date/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/End Date/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Max Teams/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Create Tournament/i })).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    const user = userEvent.setup()
    render(<TournamentForm />)
    
    const submitButton = screen.getByRole('button', { name: /Create Tournament/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Tournament name is required/i)).toBeInTheDocument()
    })
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    mockCreateTournament.mockResolvedValue({ id: 1, name: 'Test Tournament' })
    
    render(<TournamentForm />)
    
    // Fill out the form
    await user.type(screen.getByLabelText(/Tournament Name/i), 'Test Tournament')
    await user.type(screen.getByLabelText(/Description/i), 'A test tournament')
    await user.type(screen.getByLabelText(/Start Date/i), '2024-01-01')
    await user.type(screen.getByLabelText(/End Date/i), '2024-01-02')
    await user.type(screen.getByLabelText(/Max Teams/i), '16')
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Create Tournament/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(mockCreateTournament).toHaveBeenCalledWith({
        name: 'Test Tournament',
        description: 'A test tournament',
        start_date: '2024-01-01',
        end_date: '2024-01-02',
        max_teams: 16,
        status: 'setup',
      })
    })
    
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/tournaments')
    })
  })

  it('handles API errors', async () => {
    const user = userEvent.setup()
    mockCreateTournament.mockRejectedValue(new Error('API Error'))
    
    render(<TournamentForm />)
    
    // Fill out the form
    await user.type(screen.getByLabelText(/Tournament Name/i), 'Test Tournament')
    await user.type(screen.getByLabelText(/Description/i), 'A test tournament')
    await user.type(screen.getByLabelText(/Start Date/i), '2024-01-01')
    await user.type(screen.getByLabelText(/End Date/i), '2024-01-02')
    await user.type(screen.getByLabelText(/Max Teams/i), '16')
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Create Tournament/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to create tournament/i)).toBeInTheDocument()
    })
  })

  it('validates date range', async () => {
    const user = userEvent.setup()
    render(<TournamentForm />)
    
    // Fill out form with invalid date range
    await user.type(screen.getByLabelText(/Tournament Name/i), 'Test Tournament')
    await user.type(screen.getByLabelText(/Start Date/i), '2024-01-02')
    await user.type(screen.getByLabelText(/End Date/i), '2024-01-01') // End before start
    
    const submitButton = screen.getByRole('button', { name: /Create Tournament/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/End date must be after start date/i)).toBeInTheDocument()
    })
  })

  it('validates max teams is a positive number', async () => {
    const user = userEvent.setup()
    render(<TournamentForm />)
    
    // Fill out form with invalid max teams
    await user.type(screen.getByLabelText(/Tournament Name/i), 'Test Tournament')
    await user.type(screen.getByLabelText(/Max Teams/i), '-1')
    
    const submitButton = screen.getByRole('button', { name: /Create Tournament/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Max teams must be a positive number/i)).toBeInTheDocument()
    })
  })
})
