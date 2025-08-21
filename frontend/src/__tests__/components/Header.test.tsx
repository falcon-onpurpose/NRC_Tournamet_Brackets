import React from 'react'
import { render, screen } from '@testing-library/react'
import Header from '@/components/Header'

describe('Header', () => {
  it('renders the NRC logo and title', () => {
    render(<Header />)
    
    expect(screen.getByText('NRC Tournament Program')).toBeInTheDocument()
    expect(screen.getByAltText('NRC Logo')).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    render(<Header />)
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Tournaments')).toBeInTheDocument()
    expect(screen.getByText('Teams')).toBeInTheDocument()
    expect(screen.getByText('Matches')).toBeInTheDocument()
    expect(screen.getByText('Public Display')).toBeInTheDocument()
  })

  it('has correct navigation structure', () => {
    render(<Header />)
    
    const nav = screen.getByRole('navigation')
    expect(nav).toBeInTheDocument()
    
    const links = screen.getAllByRole('link')
    expect(links).toHaveLength(5) // Dashboard, Tournaments, Teams, Matches, Public Display
  })

  it('applies correct styling classes', () => {
    render(<Header />)
    
    const header = screen.getByRole('banner')
    expect(header).toHaveClass('bg-white', 'shadow-sm', 'border-b')
    
    const logo = screen.getByAltText('NRC Logo')
    expect(logo).toHaveClass('h-8', 'w-auto')
  })
})
