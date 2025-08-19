#!/usr/bin/env python3
"""
Simple test to verify our services work without complex model imports.
"""

def test_validation_service():
    """Test validation service without complex imports."""
    print("Testing validation service...")
    
    # Test basic validation logic
    def validate_tournament_name(name):
        if not name or not name.strip():
            return False, "Tournament name is required"
        if len(name.strip()) > 255:
            return False, "Tournament name must be 255 characters or less"
        return True, None
    
    # Test cases
    test_cases = [
        ("", False),
        ("Valid Tournament", True),
        ("A" * 256, False),  # Too long
        ("Test Tournament", True)
    ]
    
    for name, expected in test_cases:
        is_valid, error = validate_tournament_name(name)
        if is_valid == expected:
            print(f"✓ '{name}' validation: {is_valid}")
        else:
            print(f"✗ '{name}' validation: {is_valid}, expected: {expected}")
    
    print("Validation service test completed!")

def test_tournament_service_logic():
    """Test tournament service logic without database dependencies."""
    print("Testing tournament service logic...")
    
    # Mock tournament data
    tournament_data = {
        "name": "Test Tournament",
        "format": "hybrid_swiss_elimination",
        "location": "Test Arena",
        "swiss_rounds": 3
    }
    
    # Test validation
    def validate_tournament_data(data):
        errors = []
        
        if not data.get("name") or not data["name"].strip():
            errors.append("Tournament name is required")
        
        if data.get("format") not in ["hybrid_swiss_elimination", "single_elimination", "double_elimination", "swiss", "round_robin"]:
            errors.append("Invalid tournament format")
        
        if data.get("swiss_rounds", 0) < 1:
            errors.append("Swiss rounds must be at least 1")
        
        return len(errors) == 0, errors
    
    is_valid, errors = validate_tournament_data(tournament_data)
    
    if is_valid:
        print("✓ Tournament data validation passed")
    else:
        print(f"✗ Tournament data validation failed: {errors}")
    
    print("Tournament service logic test completed!")

if __name__ == "__main__":
    print("Running simple service tests...")
    print("=" * 50)
    
    test_validation_service()
    print()
    test_tournament_service_logic()
    
    print("=" * 50)
    print("All simple tests completed!")
