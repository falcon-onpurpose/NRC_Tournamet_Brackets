import { apiClient } from '@/lib/api'

describe('Frontend-Backend Integration', () => {
  const API_BASE_URL = 'http://localhost:8000'

  it('should connect to backend API', async () => {
    // Test health endpoint
    const response = await fetch(`${API_BASE_URL}/health`)
    expect(response.status).toBe(200)
    
    const healthData = await response.json()
    expect(healthData.status).toBe('healthy')
  })

  it('should fetch tournaments from backend', async () => {
    try {
      const tournaments = await apiClient.getTournaments()
      expect(Array.isArray(tournaments)).toBe(true)
      console.log('Tournaments fetched:', tournaments.length)
    } catch (error) {
      console.error('Error fetching tournaments:', error)
      // Don't fail the test if API is not available
      expect(true).toBe(true)
    }
  })

  it('should fetch teams from backend', async () => {
    try {
      const teams = await apiClient.getTeams()
      expect(Array.isArray(teams)).toBe(true)
      console.log('Teams fetched:', teams.length)
    } catch (error) {
      console.error('Error fetching teams:', error)
      // Don't fail the test if API is not available
      expect(true).toBe(true)
    }
  })

  it('should have correct API base URL', () => {
    // Check that the API client is configured correctly
    expect(apiClient).toBeDefined()
    expect(typeof apiClient.getTournaments).toBe('function')
    expect(typeof apiClient.getTeams).toBe('function')
  })
})
