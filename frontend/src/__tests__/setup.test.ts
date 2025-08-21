describe('Test Setup', () => {
  it('should run tests correctly', () => {
    expect(true).toBe(true)
  })

  it('should have proper test environment', () => {
    expect(typeof window).toBe('object')
    expect(typeof document).toBe('object')
  })

  it('should have jest-dom matchers available', () => {
    const element = document.createElement('div')
    element.className = 'test-class'
    expect(element).toHaveClass('test-class')
  })
})
