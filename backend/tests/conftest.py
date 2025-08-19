"""
Shared test fixtures and configurations for NRC Tournament Program tests.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add the parent directory to the path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_session, create_db_and_tables
from config import get_settings
from models import Tournament, RobotClass, Team, Robot, Player, SwissMatch, EliminationMatch
from schemas import TournamentCreate, TeamCreate, RobotCreate


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(create_db_and_tables)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_settings():
    """Create test settings."""
    return get_settings()


@pytest.fixture
def client(test_session):
    """Create a test client with session override."""
    from main import app
    
    async def override_get_session():
        yield test_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_arena_client():
    """Create a mock arena client."""
    return AsyncMock()


@pytest.fixture
def mock_csv_import_service():
    """Create a mock CSV import service."""
    return AsyncMock()


@pytest.fixture
def sample_robot_classes():
    """Create sample robot classes for testing."""
    return [
        {
            "name": "150g - Non-Destructive",
            "weight_limit": 150,
            "match_duration": 120,
            "pit_activation_time": 60,
            "description": "Antweight non-destructive class"
        },
        {
            "name": "150g - Destructive", 
            "weight_limit": 150,
            "match_duration": 120,
            "pit_activation_time": 60,
            "description": "Antweight destructive class"
        },
        {
            "name": "Beetleweight",
            "weight_limit": 1500,
            "match_duration": 180,
            "pit_activation_time": 60,
            "description": "Beetleweight class"
        }
    ]


@pytest.fixture
async def sample_tournament(test_session):
    """Create a sample tournament for testing."""
    tournament = Tournament(
        name="Test Tournament",
        format="hybrid_swiss_elimination",
        status="setup",
        location="Test Arena",
        description="Test tournament for unit tests",
        swiss_rounds_count=3
    )
    
    test_session.add(tournament)
    await test_session.commit()
    await test_session.refresh(tournament)
    
    return tournament


@pytest.fixture
async def sample_teams(test_session, sample_tournament):
    """Create sample teams for testing."""
    teams = []
    
    for i in range(4):
        team = Team(
            tournament_id=sample_tournament.id,
            name=f"Test Team {i+1}",
            address=f"Test Address {i+1}",
            phone=f"123456789{i}",
            email=f"team{i+1}@test.com"
        )
        teams.append(team)
    
    test_session.add_all(teams)
    await test_session.commit()
    
    for team in teams:
        await test_session.refresh(team)
    
    return teams


@pytest.fixture
async def sample_robots(test_session, sample_teams):
    """Create sample robots for testing."""
    robots = []
    
    for i, team in enumerate(sample_teams):
        robot = Robot(
            team_id=team.id,
            robot_class_id=1,  # Assuming robot class 1 exists
            name=f"Test Robot {i+1}",
            weight=150.0
        )
        robots.append(robot)
    
    test_session.add_all(robots)
    await test_session.commit()
    
    for robot in robots:
        await test_session.refresh(robot)
    
    return robots


@pytest.fixture
async def sample_matches(test_session, sample_tournament, sample_teams):
    """Create sample matches for testing."""
    matches = []
    
    # Create Swiss matches
    for i in range(2):
        match = SwissMatch(
            tournament_id=sample_tournament.id,
            team1_id=sample_teams[i*2].id,
            team2_id=sample_teams[i*2+1].id,
            round_number=1,
            match_number=i+1,
            status="scheduled"
        )
        matches.append(match)
    
    test_session.add_all(matches)
    await test_session.commit()
    
    for match in matches:
        await test_session.refresh(match)
    
    return matches


@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
            return self.elapsed()
        
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Helper functions for creating test data
async def create_test_tournament(session: AsyncSession, **kwargs):
    """Helper to create a test tournament."""
    tournament_data = {
        "name": "Test Tournament",
        "format": "hybrid_swiss_elimination",
        "status": "setup",
        "location": "Test Arena",
        "description": "Test tournament",
        "swiss_rounds": 3
    }
    tournament_data.update(kwargs)
    
    tournament = Tournament(**tournament_data)
    session.add(tournament)
    await session.commit()
    await session.refresh(tournament)
    return tournament


async def create_test_teams(session: AsyncSession, tournament_id: int, count: int = 4):
    """Helper to create test teams."""
    teams = []
    
    for i in range(count):
        team = Team(
            tournament_id=tournament_id,
            name=f"Test Team {i+1}",
            address=f"Test Address {i+1}",
            phone=f"123456789{i}",
            email=f"team{i+1}@test.com"
        )
        teams.append(team)
    
    session.add_all(teams)
    await session.commit()
    
    for team in teams:
        await session.refresh(team)
    
    return teams


async def create_test_robots(session: AsyncSession, team_ids: list, robot_class_id: int = 1):
    """Helper to create test robots."""
    robots = []
    
    for i, team_id in enumerate(team_ids):
        robot = Robot(
            team_id=team_id,
            robot_class_id=robot_class_id,
            name=f"Test Robot {i+1}",
            weight=150.0
        )
        robots.append(robot)
    
    session.add_all(robots)
    await session.commit()
    
    for robot in robots:
        await session.refresh(robot)
    
    return robots
