#!/usr/bin/env python3
"""
Test refactored repository functionality (Robot, Player, RobotClass).
"""
import asyncio
import random
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

def test_robot_classes_api():
    """Test robot classes API with refactored structure."""
    print("\n🤖 Testing Refactored Robot Classes API...")
    
    # Test get all robot classes
    response = client.get("/api/v1/robot-classes/")
    assert response.status_code == 200
    robot_classes = response.json()
    print(f"✅ Listed {len(robot_classes)} robot classes")
    
    # Test get robot class by ID
    if robot_classes:
        robot_class_id = robot_classes[0]["id"]
        response = client.get(f"/api/v1/robot-classes/{robot_class_id}")
        assert response.status_code == 200
        robot_class = response.json()
        assert robot_class["id"] == robot_class_id
        print("✅ Retrieved robot class by ID")
    
    # Test robot class statistics
    response = client.get("/api/v1/robot-classes/statistics/summary")
    assert response.status_code == 200
    stats = response.json()
    assert "total_classes" in stats
    print("✅ Retrieved robot class statistics")
    
    # Test active robot classes
    response = client.get("/api/v1/robot-classes/active/all")
    assert response.status_code == 200
    active_classes = response.json()
    print(f"✅ Retrieved {len(active_classes)} active robot classes")

def test_robots_api():
    """Test robots API with refactored structure."""
    print("\n🦾 Testing Refactored Robots API...")
    
    # Test get all robots
    response = client.get("/api/v1/robots/")
    assert response.status_code == 200
    robots = response.json()
    print(f"✅ Listed {len(robots)} robots")
    
    # Test robot statistics
    response = client.get("/api/v1/robots/statistics/summary")
    assert response.status_code == 200
    stats = response.json()
    assert "total_robots" in stats
    print("✅ Retrieved robot statistics")
    
    # Test waitlisted robots
    response = client.get("/api/v1/robots/waitlist/all")
    assert response.status_code == 200
    waitlisted_robots = response.json()
    print(f"✅ Retrieved {len(waitlisted_robots)} waitlisted robots")
    
    # Test robots by class
    response = client.get("/api/v1/robots/class/1")
    assert response.status_code == 200
    class_robots = response.json()
    print(f"✅ Retrieved {len(class_robots)} robots in class 1")

def test_players_api():
    """Test players API with refactored structure."""
    print("\n👤 Testing Refactored Players API...")
    
    # Test get all players
    response = client.get("/api/v1/players/")
    assert response.status_code == 200
    players = response.json()
    print(f"✅ Listed {len(players)} players")
    
    # Test player statistics
    response = client.get("/api/v1/players/statistics/summary")
    assert response.status_code == 200
    stats = response.json()
    assert "total_players" in stats
    print("✅ Retrieved player statistics")
    
    # Test search players (should handle empty results gracefully)
    response = client.get("/api/v1/players/search/NonExistentPlayer")
    assert response.status_code == 200
    search_results = response.json()
    print(f"✅ Search returned {len(search_results)} results")

def test_repository_integration():
    """Test integration between repositories."""
    print("\n🔗 Testing Repository Integration...")
    
    # Test that all APIs work together
    apis = [
        ("Robot Classes", "/api/v1/robot-classes/"),
        ("Robots", "/api/v1/robots/"),
        ("Players", "/api/v1/players/"),
    ]
    
    for name, endpoint in apis:
        response = client.get(endpoint)
        assert response.status_code == 200
        print(f"✅ {name} API working")
    
    # Test statistics endpoints
    stats_endpoints = [
        ("Robot Classes", "/api/v1/robot-classes/statistics/summary"),
        ("Robots", "/api/v1/robots/statistics/summary"),
        ("Players", "/api/v1/players/statistics/summary"),
    ]
    
    for name, endpoint in stats_endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        stats = response.json()
        print(f"✅ {name} statistics working")

def test_repository_error_handling():
    """Test error handling in repository APIs."""
    print("\n❌ Testing Repository Error Handling...")
    
    # Test non-existent robot class
    response = client.get("/api/v1/robot-classes/999999")
    assert response.status_code == 404
    print("✅ Robot class 404 error handled correctly")
    
    # Test non-existent robot
    response = client.get("/api/v1/robots/999999")
    assert response.status_code == 404
    print("✅ Robot 404 error handled correctly")
    
    # Test non-existent player
    response = client.get("/api/v1/players/999999")
    assert response.status_code == 404
    print("✅ Player 404 error handled correctly")

def test_repository_crud_operations():
    """Test CRUD operations on repositories."""
    print("\n✏️ Testing Repository CRUD Operations...")
    
    # Note: We'll test the endpoints without actually creating/modifying data
    # to avoid interfering with existing test data
    
    # Test that POST endpoints exist and return appropriate errors for invalid data
    invalid_robot_class = {
        "name": "",  # Invalid: empty name
        "weight_limit": -1,  # Invalid: negative weight
        "match_duration": 0,  # Invalid: zero duration
        "pit_activation_time": -1  # Invalid: negative time
    }
    
    response = client.post("/api/v1/robot-classes/", json=invalid_robot_class)
    assert response.status_code in [400, 422]  # Should reject invalid data
    print("✅ Robot class validation working")
    
    # Test robot creation validation
    invalid_robot = {
        "name": "",  # Invalid: empty name
        "robot_class_id": 0,  # Invalid: zero ID
        "team_id": 0  # Invalid: zero ID
    }
    
    response = client.post("/api/v1/robots/", json=invalid_robot)
    assert response.status_code in [400, 422]  # Should reject invalid data
    print("✅ Robot validation working")
    
    # Test player creation validation
    invalid_player = {
        "first_name": "",  # Invalid: empty name
        "last_name": "",   # Invalid: empty name
        "team_id": 0       # Invalid: zero ID
    }
    
    response = client.post("/api/v1/players/", json=invalid_player)
    assert response.status_code in [400, 422]  # Should reject invalid data
    print("✅ Player validation working")

async def main():
    """Run refactored repositories tests."""
    print("🧪 Starting Refactored Repositories Test Suite...")
    print("   Testing Robot, Player, and RobotClass repositories")
    
    # Initialize database
    await init_test_database()
    
    try:
        # Run all tests
        test_health_endpoint()
        test_robot_classes_api()
        test_robots_api()
        test_players_api()
        test_repository_integration()
        test_repository_error_handling()
        test_repository_crud_operations()
        
        print("\n🎉 All refactored repository tests passed!")
        print("✅ Refactored repository structure is working correctly")
        print("   - Robot Classes API (refactored) ✅")
        print("   - Robots API (refactored) ✅")
        print("   - Players API (refactored) ✅")
        print("   - Repository integration ✅")
        print("   - Error handling ✅")
        print("   - CRUD operations ✅")
        print("   - Statistics endpoints ✅")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
