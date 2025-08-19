#!/usr/bin/env python3
"""
Test refactored matches functionality.
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

def test_matches_endpoints():
    """Test matches endpoints with refactored structure."""
    print("\n⚔️ Testing Matches Endpoints (Refactored)...")
    
    # List Swiss matches (should be empty initially)
    response = client.get("/api/v1/matches/swiss")
    assert response.status_code == 200
    matches = response.json()
    print(f"✅ Listed {len(matches)} Swiss matches")
    
    # List elimination matches (should be empty initially)
    response = client.get("/api/v1/matches/elimination")
    assert response.status_code == 200
    matches = response.json()
    print(f"✅ Listed {len(matches)} elimination matches")
    
    # Get pending matches (should be empty initially)
    response = client.get("/api/v1/matches/pending")
    assert response.status_code == 200
    pending_matches = response.json()
    print(f"✅ Retrieved {len(pending_matches)} pending matches")
    
    # Get match statistics
    response = client.get("/api/v1/matches/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert "swiss_matches" in stats
    assert "elimination_matches" in stats
    print("✅ Retrieved match statistics")
    
    # Test creating a Swiss match (requires tournament and teams)
    # For now, we'll test with invalid data to verify validation
    invalid_swiss_match = {
        "tournament_id": 0,  # Invalid tournament ID
        "team1_id": 0,       # Invalid team ID
        "team2_id": 0,       # Invalid team ID
        "round_number": 0    # Invalid round number
    }
    
    response = client.post("/api/v1/matches/swiss", json=invalid_swiss_match)
    assert response.status_code == 400
    print("✅ Swiss match validation working")
    
    # Test creating an elimination match (requires tournament, teams, and bracket)
    invalid_elim_match = {
        "tournament_id": 0,  # Invalid tournament ID
        "team1_id": 0,       # Invalid team ID
        "team2_id": 0,       # Invalid team ID
        "bracket_id": 0,     # Invalid bracket ID
        "round_number": 0    # Invalid round number
    }
    
    response = client.post("/api/v1/matches/elimination", json=invalid_elim_match)
    assert response.status_code == 400
    print("✅ Elimination match validation working")
    
    # Test invalid match ID
    response = client.get("/api/v1/matches/swiss/999999")
    assert response.status_code == 404
    print("✅ 404 error for non-existent Swiss match")
    
    response = client.get("/api/v1/matches/elimination/999999")
    assert response.status_code == 404
    print("✅ 404 error for non-existent elimination match")

def test_error_handling():
    """Test error handling."""
    print("\n❌ Testing Error Handling...")
    
    # Test invalid match ID format
    response = client.get("/api/v1/matches/swiss/invalid")
    assert response.status_code == 422
    print("✅ 422 error for invalid Swiss match ID")
    
    response = client.get("/api/v1/matches/elimination/invalid")
    assert response.status_code == 422
    print("✅ 422 error for invalid elimination match ID")
    
    # Test invalid match result data
    invalid_result = {
        "winner_id": 0,      # Invalid winner ID
        "team1_score": -1,   # Invalid score
        "team2_score": -1    # Invalid score
    }
    
    response = client.post("/api/v1/matches/swiss/1/complete", json=invalid_result)
    assert response.status_code in [400, 404, 422]  # Could be 404 if match doesn't exist, or 422 for validation
    print("✅ Match result validation working")

async def main():
    """Run refactored matches tests."""
    print("🧪 Starting Refactored Matches Test Suite...")
    
    # Initialize database
    await init_test_database()
    
    try:
        # Run all tests
        test_health_endpoint()
        test_matches_endpoints()
        test_error_handling()
        
        print("\n🎉 All refactored matches tests passed!")
        print("✅ Refactored matches structure is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
