"""
Test script to verify FastAPI endpoints with database initialization.
"""

import asyncio
from fastapi.testclient import TestClient
from main import app
from database import create_db_and_tables

async def init_database():
    """Initialize the database tables."""
    await create_db_and_tables()
    print("✅ Database initialized")

def test_health_endpoint():
    """Test the health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NRC Tournament Program"
    print("✅ Health endpoint working")

def test_api_docs():
    """Test that API documentation is accessible."""
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
    print("✅ API documentation accessible")

def test_tournament_endpoints():
    """Test tournament endpoints structure."""
    client = TestClient(app)
    
    # Test GET /api/v1/tournaments/ (should return empty list initially)
    response = client.get("/api/v1/tournaments/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print("✅ Tournament list endpoint working")

def test_teams_endpoints():
    """Test teams endpoints structure."""
    client = TestClient(app)
    
    # Test GET /api/v1/teams/ (should return empty list initially)
    response = client.get("/api/v1/teams/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print("✅ Teams list endpoint working")

def test_robot_classes_endpoints():
    """Test robot classes endpoints structure."""
    client = TestClient(app)
    
    # Test GET /api/v1/robot-classes/ (should return empty list initially)
    response = client.get("/api/v1/robot-classes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print("✅ Robot classes list endpoint working")

def test_matches_endpoints():
    """Test matches endpoints structure."""
    client = TestClient(app)
    
    # Test GET /api/v1/matches/swiss (should return empty list initially)
    response = client.get("/api/v1/matches/swiss")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print("✅ Swiss matches list endpoint working")
    
    # Test GET /api/v1/matches/elimination (should return empty list initially)
    response = client.get("/api/v1/matches/elimination")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print("✅ Elimination matches list endpoint working")

def test_public_endpoints():
    """Test public display endpoints structure."""
    client = TestClient(app)
    
    # Test GET /api/v1/public/active-tournaments
    response = client.get("/api/v1/public/active-tournaments")
    assert response.status_code == 200
    data = response.json()
    assert "active_tournaments" in data
    assert "count" in data
    print("✅ Public active tournaments endpoint working")

def test_arena_endpoints():
    """Test arena integration endpoints structure."""
    client = TestClient(app)
    
    # Test GET /api/v1/arena/status
    response = client.get("/api/v1/arena/status")
    assert response.status_code == 200
    data = response.json()
    assert "arena_status" in data
    assert "connected" in data
    print("✅ Arena status endpoint working")

async def main():
    """Run all tests."""
    print("🧪 Testing FastAPI Application with Database...")
    
    try:
        # Initialize database first
        await init_database()
        
        # Run tests
        test_health_endpoint()
        test_api_docs()
        test_tournament_endpoints()
        test_teams_endpoints()
        test_robot_classes_endpoints()
        test_matches_endpoints()
        test_public_endpoints()
        test_arena_endpoints()
        
        print("\n🎉 All API tests passed! FastAPI application is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
