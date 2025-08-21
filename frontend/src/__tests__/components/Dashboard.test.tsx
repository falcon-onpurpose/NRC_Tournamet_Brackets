import React from 'react'
import { render, screen } from '@testing-library/react'
import Dashboard from '@/components/Dashboard'

// Mock the API client
jest.mock('@/lib/api', () => ({
  getTournaments: jest.fn().mockResolvedValue([]),
  getTeams: jest.fn().mockResolvedValue([]),
  getMatches: jest.fn().mockResolvedValue([]),
}))

describe('Dashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders dashboard title and welcome message', () => {
    render(<Dashboard />)
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText(/Welcome to the NRC Tournament Program/)).toBeInTheDocument()
  })

  it('renders statistics cards', () => {
    render(<Dashboard />)
    
    expect(screen.getByText('Tournaments')).toBeInTheDocument()
    expect(screen.getByText('Teams')).toBeInTheDocument()
    expect(screen.getByText('Matches')).toBeInTheDocument()
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('renders quick action buttons', () => {
    render(<Dashboard />)
    
    expect(screen.getByText('Create Tournament')).toBeInTheDocument()
    expect(screen.getByText('Register Team')).toBeInTheDocument()
    expect(screen.getByText('Schedule Match')).toBeInTheDocument()
    expect(screen.getByText('View Public Display')).toBeInTheDocument()
  })

  it('displays loading state initially', () => {
    render(<Dashboard />)
    
    // Should show loading indicators or default values
    expect(screen.getByText('0')).toBeInTheDocument() // Default tournament count
  })

  it('has correct card structure', () => {
    render(<Dashboard />)
    
    const cards = screen.getAllByTestId('stat-card')
    expect(cards).toHaveLength(4) // Tournaments, Teams, Matches, Active
  })

  it('applies correct styling classes', () => {
    render(<Dashboard />)
    
    const dashboard = screen.getByTestId('dashboard')
    expect(dashboard).toHaveClass('p-6')
    
    const statsGrid = screen.getByTestId('stats-grid')
    expect(statsGrid).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-4')
  })
})
