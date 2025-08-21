#!/usr/bin/env python3
"""
Test refactored validation functionality.
"""
import asyncio
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from main import app
from database import create_db_and_tables

# Test client
client = TestClient(app)

async def init_test_database():
    """Initialize the test database."""
    print("🔄 Initializing test database...")
    await create_db_and_tables()
    print("✅ Test database initialized")

def test_health_endpoint():
    """Test health endpoint."""
    print("\n📋 Testing Health Endpoint...")
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health endpoint working")

def test_validation_endpoints():
    """Test validation endpoints with refactored structure."""
    print("\n✅ Testing Validation Endpoints (Refactored)...")
    
    # Test tournament validation - valid data
    future_date = datetime.now() + timedelta(days=30)
    end_date = future_date + timedelta(hours=8)
    
    valid_tournament = {
        "name": "Valid Tournament",
        "description": "A valid tournament for testing",
        "start_date": future_date.isoformat(),
        "end_date": end_date.isoformat(),
        "location": "Test Location",
        "max_teams": 16,
        "swiss_rounds_count": 3
    }
    
    response = client.post("/api/v1/validation/tournament", json=valid_tournament)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == True
    assert len(result["errors"]) == 0
    print("✅ Valid tournament data validation passed")
    
    # Test tournament validation - invalid data
    invalid_tournament = {
        "name": "",  # Empty name
        "description": "Invalid tournament",
        "start_date": (datetime.now() - timedelta(days=1)).isoformat(),  # Past date
        "end_date": future_date.isoformat(),
        "location": "",  # Empty location
        "max_teams": 16,
        "swiss_rounds_count": 3
    }
    
    response = client.post("/api/v1/validation/tournament", json=invalid_tournament)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == False
    assert len(result["errors"]) > 0
    assert "Tournament name is required" in result["errors"]
    assert "Tournament location is required" in result["errors"]
    print("✅ Invalid tournament data validation failed as expected")
    
    # Test team validation - valid data
    valid_team = {
        "name": "Valid Team",
        "email": "valid@example.com",
        "tournament_id": 1
    }
    
    response = client.post("/api/v1/validation/team", json=valid_team)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == True
    assert len(result["errors"]) == 0
    print("✅ Valid team data validation passed")
    
    # Test team validation - invalid data
    invalid_team = {
        "name": "",  # Empty name
        "email": "invalid-email",  # Invalid email
        "tournament_id": 0  # Invalid tournament ID
    }
    
    response = client.post("/api/v1/validation/team", json=invalid_team)
    if response.status_code == 200:
        result = response.json()
        assert result["is_valid"] == False
        assert len(result["errors"]) > 0
        assert "Team name is required" in result["errors"]
        assert "Valid tournament ID is required" in result["errors"]
        print("✅ Invalid team data validation failed as expected")
    else:
        # FastAPI validation error (422) is also acceptable for invalid data
        assert response.status_code == 422
        print("✅ Invalid team data rejected by FastAPI validation")
    
    # Test Swiss match validation - valid data
    valid_swiss_match = {
        "tournament_id": 1,
        "team1_id": 1,
        "team2_id": 2,
        "round_number": 1
    }
    
    response = client.post("/api/v1/validation/match/swiss", json=valid_swiss_match)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == True
    assert len(result["errors"]) == 0
    print("✅ Valid Swiss match data validation passed")
    
    # Test Swiss match validation - invalid data
    invalid_swiss_match = {
        "tournament_id": 0,  # Invalid tournament ID
        "team1_id": 0,       # Invalid team ID
        "team2_id": 0,       # Invalid team ID
        "round_number": 0    # Invalid round number
    }
    
    response = client.post("/api/v1/validation/match/swiss", json=invalid_swiss_match)
    if response.status_code == 200:
        result = response.json()
        assert result["is_valid"] == False
        assert len(result["errors"]) > 0
        assert "Valid tournament ID is required" in result["errors"]
        print("✅ Invalid Swiss match data validation failed as expected")
    else:
        # FastAPI validation error (422) is also acceptable for invalid data
        assert response.status_code == 422
        print("✅ Invalid Swiss match data rejected by FastAPI validation")
    
    # Test robot validation - valid data
    valid_robot = {
        "name": "Valid Robot",
        "robot_class_id": 1,
        "comments": "A valid robot for testing"
    }
    
    response = client.post("/api/v1/validation/robot", json=valid_robot)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == True
    assert len(result["errors"]) == 0
    print("✅ Valid robot data validation passed")
    
    # Test robot validation - invalid data
    invalid_robot = {
        "name": "",  # Empty name
        "robot_class_id": 0,  # Invalid robot class ID
        "comments": "x" * 1001  # Too long comments
    }
    
    response = client.post("/api/v1/validation/robot", json=invalid_robot)
    if response.status_code == 200:
        result = response.json()
        assert result["is_valid"] == False
        assert len(result["errors"]) > 0
        assert "Robot name is required" in result["errors"]
        print("✅ Invalid robot data validation failed as expected")
    else:
        # FastAPI validation error (422) is also acceptable for invalid data
        assert response.status_code == 422
        print("✅ Invalid robot data rejected by FastAPI validation")
    
    # Test player validation - valid data
    valid_player = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    }
    
    response = client.post("/api/v1/validation/player", json=valid_player)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == True
    assert len(result["errors"]) == 0
    print("✅ Valid player data validation passed")
    
    # Test player validation - invalid data
    invalid_player = {
        "first_name": "",  # Empty first name
        "last_name": "",   # Empty last name
        "email": "invalid-email"  # Invalid email
    }
    
    response = client.post("/api/v1/validation/player", json=invalid_player)
    if response.status_code == 200:
        result = response.json()
        assert result["is_valid"] == False
        assert len(result["errors"]) > 0
        assert "Player first name is required" in result["errors"]
        assert "Player last name is required" in result["errors"]
        print("✅ Invalid player data validation failed as expected")
    else:
        # FastAPI validation error (422) is also acceptable for invalid data
        assert response.status_code == 422
        print("✅ Invalid player data rejected by FastAPI validation")
    
    # Test CSV validation - valid data
    valid_csv_data = {
        "csv_content": "Team,Robot_Name,Robot_Weightclass\nTeam1,Robot1,3lb\nTeam2,Robot2,12lb"
    }
    
    response = client.post("/api/v1/validation/csv", json=valid_csv_data)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == True
    assert len(result["errors"]) == 0
    print("✅ Valid CSV data validation passed")
    
    # Test CSV validation - invalid data
    invalid_csv_data = {
        "csv_content": "InvalidHeader\nData1"
    }
    
    response = client.post("/api/v1/validation/csv", json=invalid_csv_data)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == False
    assert len(result["errors"]) > 0
    print("✅ Invalid CSV data validation failed as expected")

def test_error_handling():
    """Test error handling."""
    print("\n❌ Testing Error Handling...")
    
    # Test malformed JSON
    response = client.post("/api/v1/validation/tournament", json={"invalid": "data"})
    assert response.status_code in [400, 422, 500]  # Could be various error codes
    print("✅ Malformed data handled correctly")

async def main():
    """Run refactored validation tests."""
    print("🧪 Starting Refactored Validation Test Suite...")
    
    # Initialize database
    await init_test_database()
    
    try:
        # Run all tests
        test_health_endpoint()
        test_validation_endpoints()
        test_error_handling()
        
        print("\n🎉 All refactored validation tests passed!")
        print("✅ Refactored validation structure is working correctly")
        print("   - Tournament validation ✅")
        print("   - Team validation ✅")
        print("   - Match validation ✅")
        print("   - Robot validation ✅")
        print("   - Player validation ✅")
        print("   - CSV validation ✅")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
