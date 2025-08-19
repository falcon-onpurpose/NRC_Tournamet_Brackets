"""
Debug script to see what's causing the 422 error.
"""

from fastapi.testclient import TestClient
from main import app

def debug_tournament_endpoint():
    """Debug the tournament endpoint."""
    client = TestClient(app)
    response = client.get("/api/v1/tournaments/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 422:
        print("422 Unprocessable Entity - likely a dependency injection issue")

if __name__ == "__main__":
    debug_tournament_endpoint()
