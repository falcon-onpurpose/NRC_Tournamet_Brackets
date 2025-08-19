# NRC Tournament Program - Modular Design & Testing Strategy

## 1. Modular Architecture Overview

### 1.1 Core Design Principles
- **Loose Coupling**: Modules communicate through well-defined interfaces
- **High Cohesion**: Related functionality grouped within modules
- **Dependency Injection**: External dependencies injected, not hardcoded
- **Interface Segregation**: Small, focused interfaces for specific use cases
- **Single Responsibility**: Each module has one clear purpose

### 1.2 Module Hierarchy
```
┌─────────────────────────────────────────────────────────────┐
│                    Tournament System                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Web API   │  │  Business   │  │   Data      │         │
│  │   Layer     │  │   Logic     │  │   Access    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Arena     │  │   CSV       │  │   Real-time │         │
│  │ Integration │  │   Import    │  │   Updates   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Config    │  │   Logging   │  │   Security  │         │
│  │ Management  │  │   System    │  │   & Auth    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 2. Module Definitions

### 2.1 Core Modules

#### Module: `tournament_core`
**Purpose**: Core tournament business logic and domain models
**Responsibilities**:
- Tournament creation and management
- Match scheduling and progression
- Bracket generation (Swiss + Elimination)
- Score calculation and standings
- Robot class management

**Interfaces**:
```python
class TournamentService:
    async def create_tournament(self, data: TournamentCreate) -> Tournament
    async def get_tournament(self, id: int) -> Tournament
    async def update_tournament(self, id: int, data: TournamentUpdate) -> Tournament
    async def delete_tournament(self, id: int) -> bool
    async def generate_brackets(self, tournament_id: int) -> List[Match]
    async def update_match_result(self, match_id: int, winner_id: int, scores: Dict) -> Match

class MatchService:
    async def create_swiss_match(self, data: SwissMatchCreate) -> SwissMatch
    async def create_elimination_match(self, data: EliminationMatchCreate) -> EliminationMatch
    async def get_upcoming_matches(self, tournament_id: int) -> List[Match]
    async def get_match_history(self, tournament_id: int) -> List[Match]
```

#### Module: `team_management`
**Purpose**: Team and robot registration management
**Responsibilities**:
- Team registration and updates
- Robot management within teams
- Player information management
- CSV import processing
- Waitlist and fee status tracking

**Interfaces**:
```python
class TeamService:
    async def create_team(self, data: TeamCreate) -> Team
    async def get_team(self, id: int) -> Team
    async def update_team(self, id: int, data: TeamUpdate) -> Team
    async def delete_team(self, id: int) -> bool
    async def get_tournament_teams(self, tournament_id: int) -> List[Team]

class RobotService:
    async def create_robot(self, data: RobotCreate) -> Robot
    async def get_robot(self, id: int) -> Robot
    async def update_robot(self, id: int, data: RobotUpdate) -> Robot
    async def get_team_robots(self, team_id: int) -> List[Robot]
```

#### Module: `data_access`
**Purpose**: Database operations and data persistence
**Responsibilities**:
- Database connection management
- CRUD operations for all entities
- Transaction management
- Query optimization
- Database migrations

**Interfaces**:
```python
class TournamentRepository:
    async def create(self, tournament: Tournament) -> Tournament
    async def get_by_id(self, id: int) -> Optional[Tournament]
    async def get_all(self, filters: Dict = None) -> List[Tournament]
    async def update(self, tournament: Tournament) -> Tournament
    async def delete(self, id: int) -> bool

class MatchRepository:
    async def create_swiss_match(self, match: SwissMatch) -> SwissMatch
    async def create_elimination_match(self, match: EliminationMatch) -> EliminationMatch
    async def get_by_tournament(self, tournament_id: int) -> List[Match]
    async def update_result(self, match_id: int, winner_id: int, scores: Dict) -> Match
```

### 2.2 Integration Modules

#### Module: `arena_integration`
**Purpose**: Communication with arena control system
**Responsibilities**:
- Arena system communication
- Match coordination
- Hazard configuration
- Status monitoring
- Error handling and fallbacks

**Interfaces**:
```python
class ArenaClient:
    async def connect(self) -> bool
    async def disconnect(self) -> None
    async def start_match(self, match_params: MatchParams) -> bool
    async def complete_match(self, match_id: int, winner_id: int) -> bool
    async def get_status(self) -> ArenaStatus
    async def configure_hazards(self, config: HazardConfig) -> bool
    async def reset_arena(self) -> bool

class ArenaStatusMonitor:
    async def start_monitoring(self) -> None
    async def stop_monitoring(self) -> None
    async def get_current_status(self) -> ArenaStatus
    async def subscribe_to_updates(self, callback: Callable) -> None
```

#### Module: `csv_import`
**Purpose**: External registration data import
**Responsibilities**:
- CSV file parsing and validation
- Data mapping and transformation
- Error handling and reporting
- Import history tracking
- Duplicate detection

**Interfaces**:
```python
class CSVImportService:
    async def import_registrations(self, csv_data: str, tournament_id: int) -> ImportResult
    async def validate_csv_format(self, csv_data: str) -> ValidationResult
    async def get_import_history(self, tournament_id: int) -> List[CSVImport]
    async def rollback_import(self, import_id: int) -> bool

class DataMapper:
    def map_robot_class(self, weightclass: str) -> RobotClass
    def map_team_data(self, row: Dict) -> TeamCreate
    def map_robot_data(self, row: Dict) -> RobotCreate
    def validate_required_fields(self, row: Dict) -> List[str]
```

### 2.3 Infrastructure Modules

#### Module: `web_api`
**Purpose**: HTTP API endpoints and request handling
**Responsibilities**:
- FastAPI application setup
- Route definitions and middleware
- Request/response handling
- CORS and security headers
- API documentation

**Interfaces**:
```python
class APIRouter:
    def include_tournament_routes(self) -> None
    def include_team_routes(self) -> None
    def include_match_routes(self) -> None
    def include_arena_routes(self) -> None
    def include_public_routes(self) -> None

class WebSocketManager:
    async def connect(self, websocket: WebSocket, client_id: str) -> None
    async def disconnect(self, client_id: str) -> None
    async def broadcast(self, message: Dict) -> None
    async def send_to_client(self, client_id: str, message: Dict) -> None
```

#### Module: `configuration`
**Purpose**: Application configuration and environment management
**Responsibilities**:
- Environment variable management
- Platform detection and optimization
- Configuration validation
- Default value management
- Environment-specific overrides

**Interfaces**:
```python
class ConfigManager:
    def get_database_config(self) -> DatabaseConfig
    def get_server_config(self) -> ServerConfig
    def get_arena_config(self) -> ArenaConfig
    def get_security_config(self) -> SecurityConfig
    def validate_config(self) -> List[str]
    def get_environment_info(self) -> Dict[str, Any]
```

#### Module: `logging`
**Purpose**: Application logging and monitoring
**Responsibilities**:
- Structured logging setup
- Log level management
- Performance monitoring
- Error tracking
- Audit trail logging

**Interfaces**:
```python
class Logger:
    def info(self, message: str, **kwargs) -> None
    def warning(self, message: str, **kwargs) -> None
    def error(self, message: str, **kwargs) -> None
    def debug(self, message: str, **kwargs) -> None
    def audit(self, action: str, user_id: str, details: Dict) -> None

class PerformanceMonitor:
    async def start_timer(self, operation: str) -> str
    async def end_timer(self, timer_id: str) -> float
    async def record_metric(self, name: str, value: float) -> None
    async def get_performance_stats(self) -> Dict[str, Any]
```

## 3. Module Dependencies

### 3.1 Dependency Graph
```
web_api
├── tournament_core
│   └── data_access
├── team_management
│   └── data_access
├── arena_integration
├── csv_import
│   └── data_access
├── configuration
└── logging

tournament_core
├── data_access
├── configuration
└── logging

team_management
├── data_access
├── csv_import
├── configuration
└── logging

arena_integration
├── configuration
└── logging

csv_import
├── data_access
├── configuration
└── logging
```

### 3.2 Dependency Injection
```python
# Example dependency injection setup
class Container:
    def __init__(self):
        self.config = ConfigManager()
        self.logger = Logger(self.config)
        self.db = DatabaseManager(self.config)
        
        # Core services
        self.tournament_repo = TournamentRepository(self.db)
        self.match_repo = MatchRepository(self.db)
        self.team_repo = TeamRepository(self.db)
        
        # Business services
        self.tournament_service = TournamentService(
            self.tournament_repo, 
            self.match_repo, 
            self.logger
        )
        self.team_service = TeamService(
            self.team_repo, 
            self.logger
        )
        
        # Integration services
        self.arena_client = ArenaClient(self.config, self.logger)
        self.csv_service = CSVImportService(self.team_repo, self.logger)
```

## 4. Testing Strategy

### 4.1 Testing Pyramid
```
        /\
       /  \     E2E Tests (Few)
      /____\    
     /      \   Integration Tests (Some)
    /________\  
   /          \ Unit Tests (Many)
  /____________\
```

### 4.2 Unit Testing Strategy

#### Module: `tournament_core`
**Test Coverage**: 95%+
**Test Types**:
- Tournament creation and validation
- Bracket generation algorithms
- Match scheduling logic
- Score calculation
- Swiss round pairing
- Elimination bracket progression

**Example Tests**:
```python
class TestTournamentService:
    async def test_create_tournament_success(self):
        # Arrange
        data = TournamentCreate(name="Test", format="hybrid_swiss_elimination")
        
        # Act
        result = await tournament_service.create_tournament(data)
        
        # Assert
        assert result.name == "Test"
        assert result.status == "setup"
        assert result.id is not None

    async def test_generate_swiss_brackets(self):
        # Arrange
        tournament = await create_test_tournament()
        teams = await create_test_teams(tournament.id, 8)
        
        # Act
        matches = await tournament_service.generate_swiss_brackets(tournament.id)
        
        # Assert
        assert len(matches) == 4  # 8 teams = 4 matches
        assert all(match.round_number == 1 for match in matches)
```

#### Module: `data_access`
**Test Coverage**: 90%+
**Test Types**:
- Database CRUD operations
- Query optimization
- Transaction management
- Connection pooling
- Error handling

**Example Tests**:
```python
class TestTournamentRepository:
    async def test_create_and_retrieve_tournament(self):
        # Arrange
        tournament = Tournament(name="Test", format="hybrid_swiss_elimination")
        
        # Act
        created = await repo.create(tournament)
        retrieved = await repo.get_by_id(created.id)
        
        # Assert
        assert retrieved.name == "Test"
        assert retrieved.id == created.id

    async def test_get_tournaments_with_filters(self):
        # Arrange
        await create_test_tournaments(5)
        
        # Act
        active_tournaments = await repo.get_all({"status": "active"})
        
        # Assert
        assert len(active_tournaments) > 0
        assert all(t.status == "active" for t in active_tournaments)
```

#### Module: `arena_integration`
**Test Coverage**: 85%+
**Test Types**:
- Arena communication protocols
- Error handling and retries
- Status monitoring
- Match coordination
- Fallback behavior

**Example Tests**:
```python
class TestArenaClient:
    async def test_start_match_success(self):
        # Arrange
        match_params = MatchParams(duration=120, pit_activation=60)
        
        # Act
        result = await arena_client.start_match(match_params)
        
        # Assert
        assert result is True
        mock_arena.assert_called_with("/api/v1/arena/start-match")

    async def test_arena_unavailable_fallback(self):
        # Arrange
        mock_arena.side_effect = ConnectionError()
        
        # Act
        result = await arena_client.start_match(match_params)
        
        # Assert
        assert result is False
        assert "Arena unavailable" in logs
```

### 4.3 Integration Testing Strategy

#### Database Integration Tests
```python
class TestDatabaseIntegration:
    async def test_tournament_with_teams_and_matches(self):
        # Arrange
        async with get_test_session() as session:
            # Create tournament
            tournament = Tournament(name="Integration Test")
            session.add(tournament)
            await session.commit()
            
            # Create teams
            team1 = Team(name="Team 1", tournament_id=tournament.id)
            team2 = Team(name="Team 2", tournament_id=tournament.id)
            session.add_all([team1, team2])
            await session.commit()
            
            # Create match
            match = SwissMatch(
                tournament_id=tournament.id,
                team1_id=team1.id,
                team2_id=team2.id
            )
            session.add(match)
            await session.commit()
            
            # Assert relationships
            result = await session.get(Tournament, tournament.id)
            assert len(result.teams) == 2
            assert len(result.swiss_matches) == 1
```

#### API Integration Tests
```python
class TestAPIIntegration:
    async def test_tournament_crud_workflow(self):
        # Create tournament
        response = await client.post("/api/v1/tournaments", json={
            "name": "API Test",
            "format": "hybrid_swiss_elimination"
        })
        assert response.status_code == 201
        tournament_id = response.json()["id"]
        
        # Get tournament
        response = await client.get(f"/api/v1/tournaments/{tournament_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "API Test"
        
        # Update tournament
        response = await client.put(f"/api/v1/tournaments/{tournament_id}", json={
            "name": "Updated API Test"
        })
        assert response.status_code == 200
        
        # Delete tournament
        response = await client.delete(f"/api/v1/tournaments/{tournament_id}")
        assert response.status_code == 204
```

### 4.4 End-to-End Testing Strategy

#### Complete Tournament Workflow
```python
class TestTournamentWorkflow:
    async def test_complete_tournament_lifecycle(self):
        # 1. Create tournament
        tournament = await create_tournament("E2E Test")
        
        # 2. Import teams
        csv_data = generate_test_csv(8)
        import_result = await csv_service.import_registrations(csv_data, tournament.id)
        assert import_result.success
        assert len(import_result.teams) == 8
        
        # 3. Generate brackets
        matches = await tournament_service.generate_brackets(tournament.id)
        assert len(matches) == 4
        
        # 4. Start first match
        match = matches[0]
        arena_result = await arena_client.start_match(match.to_params())
        assert arena_result
        
        # 5. Complete match
        await arena_client.complete_match(match.id, match.team1_id)
        updated_match = await match_service.update_result(match.id, match.team1_id, {"score": "3-1"})
        assert updated_match.winner_id == match.team1_id
        
        # 6. Verify standings
        standings = await tournament_service.get_standings(tournament.id)
        assert len(standings) == 8
        assert standings[0].team_id == match.team1_id
```

### 4.5 Performance Testing Strategy

#### Database Performance Tests
```python
class TestDatabasePerformance:
    async def test_large_tournament_performance(self):
        # Create tournament with 64 teams
        tournament = await create_tournament("Performance Test")
        teams = await create_test_teams(tournament.id, 64)
        
        # Measure bracket generation time
        start_time = time.time()
        matches = await tournament_service.generate_brackets(tournament.id)
        generation_time = time.time() - start_time
        
        # Assert performance requirements
        assert generation_time < 5.0  # Should complete within 5 seconds
        assert len(matches) == 32  # 64 teams = 32 matches
        
        # Measure standings calculation
        start_time = time.time()
        standings = await tournament_service.get_standings(tournament.id)
        standings_time = time.time() - start_time
        
        assert standings_time < 1.0  # Should complete within 1 second
```

#### API Performance Tests
```python
class TestAPIPerformance:
    async def test_concurrent_user_access(self):
        # Simulate 10 concurrent users
        async def user_workflow(user_id: int):
            # Create tournament
            response = await client.post("/api/v1/tournaments", json={
                "name": f"User {user_id} Tournament"
            })
            assert response.status_code == 201
            
            # Get tournaments
            response = await client.get("/api/v1/tournaments")
            assert response.status_code == 200
            
            # Update tournament
            tournament_id = response.json()[0]["id"]
            response = await client.put(f"/api/v1/tournaments/{tournament_id}", json={
                "name": f"Updated User {user_id} Tournament"
            })
            assert response.status_code == 200
        
        # Run concurrent workflows
        start_time = time.time()
        await asyncio.gather(*[user_workflow(i) for i in range(10)])
        total_time = time.time() - start_time
        
        # Assert performance requirements
        assert total_time < 30.0  # Should complete within 30 seconds
```

## 5. Testing Infrastructure

### 5.1 Test Environment Setup
```python
# conftest.py
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(test_session):
    from main import app
    from fastapi.testclient import TestClient
    app.dependency_overrides[get_session] = lambda: test_session
    with TestClient(app) as client:
        yield client
```

### 5.2 Mock Services
```python
# mocks.py
class MockArenaClient:
    def __init__(self):
        self.calls = []
        self.responses = {}
    
    async def start_match(self, params):
        self.calls.append(("start_match", params))
        return self.responses.get("start_match", True)
    
    async def get_status(self):
        self.calls.append(("get_status", None))
        return self.responses.get("get_status", ArenaStatus.IDLE)

class MockCSVImportService:
    def __init__(self):
        self.imports = []
    
    async def import_registrations(self, csv_data, tournament_id):
        result = ImportResult(success=True, teams_created=8)
        self.imports.append((csv_data, tournament_id, result))
        return result
```

### 5.3 Test Data Factories
```python
# factories.py
class TournamentFactory:
    @staticmethod
    def create_tournament(**kwargs) -> TournamentCreate:
        defaults = {
            "name": "Test Tournament",
            "format": "hybrid_swiss_elimination",
            "location": "Test Arena",
            "description": "Test tournament for testing"
        }
        defaults.update(kwargs)
        return TournamentCreate(**defaults)

class TeamFactory:
    @staticmethod
    def create_team(**kwargs) -> TeamCreate:
        defaults = {
            "name": "Test Team",
            "address": "Test Address",
            "phone": "1234567890",
            "email": "test@example.com"
        }
        defaults.update(kwargs)
        return TeamCreate(**defaults)
```

## 6. Continuous Testing Strategy

### 6.1 Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### 6.2 CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 .
        black --check .
        isort --check-only .
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ --cov=. --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 6.3 Test Coverage Requirements
- **Unit Tests**: 90%+ coverage for all modules
- **Integration Tests**: 80%+ coverage for critical workflows
- **E2E Tests**: All major user journeys covered
- **Performance Tests**: All performance requirements validated

## 7. Module Development Workflow

### 7.1 Development Phases
1. **Interface Definition**: Define module interfaces and contracts
2. **Unit Tests**: Write comprehensive unit tests
3. **Implementation**: Implement module functionality
4. **Integration Tests**: Test module integration
5. **Documentation**: Update module documentation
6. **Review**: Code review and testing validation

### 7.2 Module Testing Checklist
- [ ] All public methods have unit tests
- [ ] Edge cases and error conditions tested
- [ ] Integration tests with dependent modules
- [ ] Performance tests for critical operations
- [ ] Documentation updated
- [ ] Code review completed
- [ ] All tests passing
- [ ] Coverage requirements met

### 7.3 Breaking Change Protocol
1. **Identify Impact**: Assess which modules are affected
2. **Update Interfaces**: Modify interfaces with backward compatibility
3. **Update Tests**: Modify all affected tests
4. **Integration Testing**: Test all dependent modules
5. **Documentation**: Update all relevant documentation
6. **Deployment**: Deploy with proper versioning

This modular design ensures that each component can be developed, tested, and maintained independently while providing clear interfaces for integration. The comprehensive testing strategy guarantees that working components remain functional as the system evolves.
