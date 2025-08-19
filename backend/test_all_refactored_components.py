#!/usr/bin/env python3
"""
Comprehensive test for all refactored components working together.
"""
import asyncio
import io
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

def test_all_refactored_components():
    """Test all refactored components working together."""
    print("\n🔗 Testing All Refactored Components Integration...")
    
    # Test 1: Teams API (refactored)
    print("\n👥 Testing Refactored Teams API...")
    response = client.get("/api/v1/teams/")
    assert response.status_code == 200
    teams = response.json()
    print(f"✅ Teams API working - {len(teams)} teams found")
    
    # Test 2: Matches API (refactored)
    print("\n⚔️ Testing Refactored Matches API...")
    response = client.get("/api/v1/matches/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert "swiss_matches" in stats
    assert "elimination_matches" in stats
    print("✅ Matches API working - statistics retrieved")
    
    # Test 3: Validation API (refactored)
    print("\n🔍 Testing Refactored Validation API...")
    
    # Test team validation
    team_data = {
        "name": "Integration Test Team",
        "tournament_id": 1
    }
    response = client.post("/api/v1/validation/team", json=team_data)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == True
    print("✅ Team validation working")
    
    # Test tournament validation
    future_date = datetime.now() + timedelta(days=30)
    end_date = future_date + timedelta(hours=8)
    tournament_data = {
        "name": "Integration Tournament",
        "description": "Test tournament for integration",
        "start_date": future_date.isoformat(),
        "end_date": end_date.isoformat(),
        "location": "Integration Test Location",
        "max_teams": 16,
        "swiss_rounds_count": 3
    }
    response = client.post("/api/v1/validation/tournament", json=tournament_data)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == True
    print("✅ Tournament validation working")
    
    # Test 4: CSV Import API (refactored)
    print("\n📊 Testing Refactored CSV Import API...")
    
    # Test sample CSV endpoint
    response = client.post("/api/v1/csv-import/sample")
    assert response.status_code == 200
    sample_data = response.json()
    assert "sample_csv" in sample_data
    print("✅ CSV sample endpoint working")
    
    # Test CSV validation
    valid_csv = """Team,Robot_Name,Robot_Weightclass,First_Name,Last_Name,Email
Integration Team 1,Integration Robot 1,150g - Non-Destructive,Integration,User1,integration1@example.com
Integration Team 2,Integration Robot 2,Beetleweight,Integration,User2,integration2@example.com"""
    
    csv_file = io.StringIO(valid_csv)
    files = {"csv_file": ("integration.csv", csv_file.getvalue(), "text/csv")}
    
    response = client.post("/api/v1/csv-import/validate", files=files)
    assert response.status_code == 200
    validation_result = response.json()
    assert validation_result["valid"] == True
    print("✅ CSV validation working")
    
    # Test 5: Create and manage teams using refactored APIs
    print("\n🏗️ Testing Team Creation and Management...")
    
    unique_id = random.randint(1000, 9999)
    team1_data = {
        "name": f"Integration Team 1 {unique_id}",
        "email": "integration1@test.com",
        "tournament_id": 1
    }
    
    # Create team
    response = client.post("/api/v1/teams/", json=team1_data)
    assert response.status_code == 201
    team1 = response.json()
    team1_id = team1["id"]
    print(f"✅ Created team with ID {team1_id}")
    
    # Update team
    update_data = {"email": "updated-integration1@test.com"}
    response = client.put(f"/api/v1/teams/{team1_id}", json=update_data)
    assert response.status_code == 200
    updated_team = response.json()
    assert updated_team["email"] == update_data["email"]
    print("✅ Updated team successfully")
    
    # Get teams by tournament
    response = client.get(f"/api/v1/teams/tournament/1")
    assert response.status_code == 200
    tournament_teams = response.json()
    team_ids = [team["id"] for team in tournament_teams]
    assert team1_id in team_ids
    print("✅ Retrieved teams by tournament")
    
    # Test 6: Test validation with real data
    print("\n✅ Testing Validation with Real Data...")
    
    # Validate the created team data
    response = client.post("/api/v1/validation/team", json=team1_data)
    assert response.status_code == 200
    result = response.json()
    assert result["is_valid"] == True
    print("✅ Team validation with real data working")
    
    # Test 7: Test error handling across all components
    print("\n❌ Testing Error Handling Across Components...")
    
    # Test duplicate team name
    duplicate_team = {
        "name": team1_data["name"],  # Same name as team1
        "email": "duplicate@test.com",
        "tournament_id": 1
    }
    
    response = client.post("/api/v1/teams/", json=duplicate_team)
    assert response.status_code == 400
    print("✅ Duplicate team validation working")
    
    # Test invalid validation data
    invalid_team = {
        "name": "",  # Empty name
        "tournament_id": 0  # Invalid tournament ID
    }
    
    response = client.post("/api/v1/validation/team", json=invalid_team)
    if response.status_code == 200:
        result = response.json()
        assert result["is_valid"] == False
        print("✅ Invalid team validation working")
    else:
        # FastAPI validation error is also acceptable
        assert response.status_code == 422
        print("✅ Invalid team data rejected by FastAPI")
    
    # Test 8: Clean up
    print("\n🧹 Cleaning up test data...")
    
    response = client.delete(f"/api/v1/teams/{team1_id}")
    assert response.status_code == 200
    print("✅ Deleted test team")
    
    return team1_id

def test_component_isolation():
    """Test that components are properly isolated."""
    print("\n🔒 Testing Component Isolation...")
    
    # Test that each API works independently
    apis = [
        ("Teams", "/api/v1/teams/"),
        ("Matches", "/api/v1/matches/statistics"),
        ("Validation", "/api/v1/validation/team"),
        ("CSV Import", "/api/v1/csv-import/sample")
    ]
    
    for name, endpoint in apis:
        try:
            if endpoint == "/api/v1/teams/":
                response = client.get(endpoint)
            elif endpoint == "/api/v1/matches/statistics":
                response = client.get(endpoint)
            elif endpoint == "/api/v1/validation/team":
                response = client.post(endpoint, json={"name": "test", "tournament_id": 1})
            elif endpoint == "/api/v1/csv-import/sample":
                response = client.post(endpoint)
            
            assert response.status_code in [200, 201, 422]  # 422 is acceptable for validation endpoints
            print(f"✅ {name} API isolated and working")
        except Exception as e:
            print(f"❌ {name} API failed: {e}")
            raise

async def main():
    """Run comprehensive refactored components test."""
    print("🧪 Starting Comprehensive Refactored Components Test Suite...")
    print("   Testing all refactored components working together")
    
    # Initialize database
    await init_test_database()
    
    try:
        # Run all tests
        test_health_endpoint()
        team_id = test_all_refactored_components()
        test_component_isolation()
        
        print("\n🎉 All refactored components tests passed!")
        print("✅ All refactored components working together correctly")
        print("   - Teams API (refactored) ✅")
        print("   - Matches API (refactored) ✅")
        print("   - Validation API (refactored) ✅")
        print("   - CSV Import API (refactored) ✅")
        print("   - Component integration ✅")
        print("   - Error handling ✅")
        print("   - Component isolation ✅")
        print(f"   - Created and managed team: {team_id}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
