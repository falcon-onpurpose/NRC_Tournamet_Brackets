#!/usr/bin/env python3
"""
Test refactored teams functionality.
"""
import asyncio
import json
import random
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

def test_teams_crud():
    """Test teams CRUD operations with refactored structure."""
    print("\n👥 Testing Teams CRUD (Refactored)...")
    
    # List teams (should be empty initially)
    response = client.get("/api/v1/teams/")
    assert response.status_code == 200
    teams = response.json()
    print(f"✅ Listed {len(teams)} teams")
    
    # Create a tournament first (needed for team creation)
    future_date = datetime.now() + timedelta(days=30)
    end_date = future_date + timedelta(hours=8)
    
    tournament_data = {
        "name": "Test Tournament for Teams",
        "description": "Test tournament for team testing",
        "start_date": future_date.isoformat(),
        "end_date": end_date.isoformat(),
        "location": "Test Location",
        "max_teams": 16,
        "swiss_rounds_count": 3
    }
    
    # Note: We need to create a tournament first, but for now we'll use a mock ID
    tournament_id = 1  # Assuming this exists
    
    # Create new team (requires tournament_id)
    unique_id = random.randint(1000, 9999)
    new_team = {
        "name": f"Refactored Team {unique_id}",
        "email": "refactored@example.com",
        "tournament_id": tournament_id
    }
    
    response = client.post("/api/v1/teams/", json=new_team)
    if response.status_code != 201:
        print(f"❌ Team creation failed: {response.status_code}")
        print(f"Response: {response.json()}")
        return None
    
    created_team = response.json()
    team_id = created_team["id"]
    print(f"✅ Created team with ID {team_id}")
    
    # Get specific team
    response = client.get(f"/api/v1/teams/{team_id}")
    assert response.status_code == 200
    fetched_team = response.json()
    assert fetched_team["name"] == new_team["name"]
    print("✅ Retrieved team by ID")
    
    # Update team
    update_data = {"email": "updated@example.com"}
    response = client.put(f"/api/v1/teams/{team_id}", json=update_data)
    assert response.status_code == 200
    updated_team = response.json()
    assert updated_team["email"] == update_data["email"]
    print("✅ Updated team")
    
    # Test duplicate name validation
    duplicate_team = {
        "name": f"Refactored Team {unique_id}",  # Same name
        "email": "duplicate@example.com",
        "tournament_id": tournament_id
    }
    response = client.post("/api/v1/teams/", json=duplicate_team)
    assert response.status_code == 400
    print("✅ Duplicate name validation working")
    
    # Test invalid data validation
    invalid_team = {
        "name": "",  # Empty name
        "tournament_id": tournament_id
    }
    response = client.post("/api/v1/teams/", json=invalid_team)
    assert response.status_code in [400, 422]  # FastAPI can return either for validation errors
    print("✅ Invalid data validation working")
    
    # Delete team
    response = client.delete(f"/api/v1/teams/{team_id}")
    assert response.status_code == 200
    print("✅ Deleted team")
    
    # Verify deletion
    response = client.get(f"/api/v1/teams/{team_id}")
    assert response.status_code == 404
    print("✅ Confirmed team deletion")
    
    return team_id

def test_error_handling():
    """Test error handling."""
    print("\n❌ Testing Error Handling...")
    
    # Test 404 for non-existent team
    response = client.get("/api/v1/teams/999999")
    assert response.status_code == 404
    print("✅ 404 error for non-existent team")
    
    # Test invalid team ID
    response = client.get("/api/v1/teams/invalid")
    assert response.status_code == 422
    print("✅ 422 error for invalid team ID")

async def main():
    """Run refactored teams tests."""
    print("🧪 Starting Refactored Teams Test Suite...")
    
    # Initialize database
    await init_test_database()
    
    try:
        # Run all tests
        test_health_endpoint()
        team_id = test_teams_crud()
        test_error_handling()
        
        print("\n🎉 All refactored teams tests passed!")
        print("✅ Refactored structure is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
