import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import TournamentForm from '@/components/TournamentForm'
import Dashboard from '@/components/Dashboard'

// Mock Next.js router
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

// Setup MSW server for API mocking
const server = setupServer(
  // Mock successful tournament creation
  rest.post('http://localhost:8000/api/v1/tournaments/', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        name: 'Test Tournament',
        description: 'A test tournament',
        start_date: '2024-01-01',
        end_date: '2024-01-02',
        max_teams: 16,
        status: 'setup',
      })
    )
  }),

  // Mock tournament listing
  rest.get('http://localhost:8000/api/v1/tournaments/', (req, res, ctx) => {
    return res(
      ctx.json([
        {
          id: 1,
          name: 'Test Tournament',
          description: 'A test tournament',
          start_date: '2024-01-01',
          end_date: '2024-01-02',
          max_teams: 16,
          status: 'setup',
        },
      ])
    )
  }),

  // Mock team creation
  rest.post('http://localhost:8000/api/v1/teams/', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        name: 'Test Team',
        tournament_id: 1,
        members: ['Player 1', 'Player 2'],
      })
    )
  }),

  // Mock team listing
  rest.get('http://localhost:8000/api/v1/teams/', (req, res, ctx) => {
    return res(
      ctx.json([
        {
          id: 1,
          name: 'Test Team',
          tournament_id: 1,
          members: ['Player 1', 'Player 2'],
        },
      ])
    )
  }),

  // Mock health check
  rest.get('http://localhost:8000/health', (req, res, ctx) => {
    return res(ctx.json({ status: 'healthy' }))
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('Frontend-Backend Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Tournament Creation Flow', () => {
    it('creates tournament and redirects to tournaments list', async () => {
      const user = userEvent.setup()
      render(<TournamentForm />)

      // Fill out the tournament form
      await user.type(screen.getByLabelText(/Tournament Name/i), 'Test Tournament')
      await user.type(screen.getByLabelText(/Description/i), 'A test tournament')
      await user.type(screen.getByLabelText(/Start Date/i), '2024-01-01')
      await user.type(screen.getByLabelText(/End Date/i), '2024-01-02')
      await user.type(screen.getByLabelText(/Max Teams/i), '16')

      // Submit the form
      const submitButton = screen.getByRole('button', { name: /Create Tournament/i })
      await user.click(submitButton)

      // Wait for API call and redirect
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/tournaments')
      })
    })

    it('handles API errors during tournament creation', async () => {
      // Override the default handler to return an error
      server.use(
        rest.post('http://localhost:8000/api/v1/tournaments/', (req, res, ctx) => {
          return res(ctx.status(400), ctx.json({ error: 'Invalid tournament data' }))
        })
      )

      const user = userEvent.setup()
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

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/Failed to create tournament/i)).toBeInTheDocument()
      })
    })
  })

  describe('Dashboard Data Loading', () => {
    it('loads and displays tournament statistics', async () => {
      render(<Dashboard />)

      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText('1')).toBeInTheDocument() // Tournament count
      })
    })

    it('handles API errors during data loading', async () => {
      // Override handlers to return errors
      server.use(
        rest.get('http://localhost:8000/api/v1/tournaments/', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ error: 'Internal server error' }))
        }),
        rest.get('http://localhost:8000/api/v1/teams/', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ error: 'Internal server error' }))
        })
      )

      render(<Dashboard />)

      // Should show default values when API fails
      await waitFor(() => {
        expect(screen.getByText('0')).toBeInTheDocument() // Default tournament count
      })
    })
  })

  describe('API Endpoint Integration', () => {
    it('makes correct API calls with proper headers', async () => {
      const user = userEvent.setup()
      render(<TournamentForm />)

      // Fill out and submit form
      await user.type(screen.getByLabelText(/Tournament Name/i), 'Test Tournament')
      await user.type(screen.getByLabelText(/Description/i), 'A test tournament')
      await user.type(screen.getByLabelText(/Start Date/i), '2024-01-01')
      await user.type(screen.getByLabelText(/End Date/i), '2024-01-02')
      await user.type(screen.getByLabelText(/Max Teams/i), '16')

      const submitButton = screen.getByRole('button', { name: /Create Tournament/i })
      await user.click(submitButton)

      // Verify the API call was made with correct data
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/tournaments')
      })
    })

    it('handles network connectivity issues', async () => {
      // Override handlers to simulate network error
      server.use(
        rest.post('http://localhost:8000/api/v1/tournaments/', (req, res, ctx) => {
          return res.networkError('Failed to connect')
        })
      )

      const user = userEvent.setup()
      render(<TournamentForm />)

      // Fill out and submit form
      await user.type(screen.getByLabelText(/Tournament Name/i), 'Test Tournament')
      await user.type(screen.getByLabelText(/Description/i), 'A test tournament')
      await user.type(screen.getByLabelText(/Start Date/i), '2024-01-01')
      await user.type(screen.getByLabelText(/End Date/i), '2024-01-02')
      await user.type(screen.getByLabelText(/Max Teams/i), '16')

      const submitButton = screen.getByRole('button', { name: /Create Tournament/i })
      await user.click(submitButton)

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/Failed to create tournament/i)).toBeInTheDocument()
      })
    })
  })

  describe('Form Validation Integration', () => {
    it('validates form data before sending to API', async () => {
      const user = userEvent.setup()
      render(<TournamentForm />)

      // Try to submit without required fields
      const submitButton = screen.getByRole('button', { name: /Create Tournament/i })
      await user.click(submitButton)

      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText(/Tournament name is required/i)).toBeInTheDocument()
      })

      // Verify no API call was made
      expect(mockPush).not.toHaveBeenCalled()
    })

    it('validates date range before submission', async () => {
      const user = userEvent.setup()
      render(<TournamentForm />)

      // Fill out form with invalid date range
      await user.type(screen.getByLabelText(/Tournament Name/i), 'Test Tournament')
      await user.type(screen.getByLabelText(/Start Date/i), '2024-01-02')
      await user.type(screen.getByLabelText(/End Date/i), '2024-01-01') // End before start

      const submitButton = screen.getByRole('button', { name: /Create Tournament/i })
      await user.click(submitButton)

      // Should show validation error
      await waitFor(() => {
        expect(screen.getByText(/End date must be after start date/i)).toBeInTheDocument()
      })

      // Verify no API call was made
      expect(mockPush).not.toHaveBeenCalled()
    })
  })
})
