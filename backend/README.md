# NRC Tournament Program - Backend

## Overview
FastAPI backend for the NRC Tournament Program, providing tournament management, arena integration, and real-time collaboration features.

## Features
- **Tournament Management**: Hybrid Swiss + Double Elimination format
- **Robot Class Support**: Antweight, Beetleweight with configurable timing
- **Multi-Class Tournaments**: Simultaneous class management with alternating rounds
- **Arena Integration**: Real-time communication with arena control system
- **CSV Import**: robotcombatevents.com registration integration
- **Multi-User Access**: Real-time collaboration with conflict resolution
- **Cross-Platform**: Works on Windows, macOS, Linux, Raspberry Pi

## Environment Setup

### ⚠️ IMPORTANT: Virtual Environment Required
This project uses a dedicated virtual environment to avoid conflicts with global Python packages. **Never use the global pyenv environment for this project.**

### Prerequisites
- Python 3.8+
- Virtual environment (created automatically)
- Database (SQLite for development, PostgreSQL for production)

### Quick Start with Virtual Environment

```bash
# Navigate to the backend directory
cd "NRC Tournament Program/backend"

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (for testing and development)
pip install -r requirements-dev.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from database import create_db_and_tables; create_db_and_tables()"

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Management

#### Activating the Environment
```bash
# Always activate the environment before working on the project
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

#### Deactivating the Environment
```bash
# When done working on the project
deactivate
```

#### Checking Environment Status
```bash
# Verify you're using the project's virtual environment
which python  # Should show path to venv/bin/python
pip list      # Should show only project dependencies
```

#### Updating Dependencies
```bash
# Update production dependencies
pip install -r requirements.txt --upgrade

# Update development dependencies
pip install -r requirements-dev.txt --upgrade

# Update specific package
pip install package_name --upgrade
```

#### Environment Troubleshooting
```bash
# If environment is corrupted, recreate it
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Installation

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd "NRC Tournament Program/backend"
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Environment**
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

6. **Initialize Database**
   ```bash
   python -c "from database import create_db_and_tables; create_db_and_tables()"
   ```

7. **Run Application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Environment Configuration
Create a `.env` file with the following variables:
```env
# Database
DATABASE_URL=sqlite:///./nrc_tournament.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/nrc_tournament

# Security
SECRET_KEY=your-secret-key-change-in-production

# Arena Integration
ARENA_API_URL=http://localhost:8001
ARENA_API_KEY=arena-api-key

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Platform Detection (auto-detected)
PLATFORM=unknown
IS_RASPBERRY_PI=false
```

## Development Workflow

### Starting Development Session
```bash
# 1. Navigate to project
cd "NRC Tournament Program/backend"

# 2. Activate environment
source venv/bin/activate

# 3. Verify environment
which python  # Should show venv path
pip list      # Should show project packages

# 4. Start development
# Your development commands here...
```

### Running Tests
```bash
# Make sure environment is activated
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_tournament_service.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run linting
flake8 .
black --check .
isort --check-only .
```

### Code Quality
```bash
# Format code
black .
isort .

# Type checking
mypy .

# Security scanning
bandit -r .
```

## API Documentation

### Core Endpoints

#### Tournament Management
```http
POST   /api/v1/tournaments          # Create tournament
GET    /api/v1/tournaments          # List tournaments
GET    /api/v1/tournaments/{id}     # Get tournament
PUT    /api/v1/tournaments/{id}     # Update tournament
DELETE /api/v1/tournaments/{id}     # Delete tournament
```

#### Robot Class Management
```http
POST   /api/v1/robot-classes        # Create robot class
GET    /api/v1/robot-classes        # List robot classes
PUT    /api/v1/robot-classes/{id}   # Update robot class
DELETE /api/v1/robot-classes/{id}   # Delete robot class
```

#### Team Registration
```http
POST   /api/v1/teams                # Create team
GET    /api/v1/teams                # List teams
PUT    /api/v1/teams/{id}           # Update team
DELETE /api/v1/teams/{id}           # Delete team
POST   /api/v1/teams/import-csv     # Import teams from CSV
```

#### Match Management
```http
POST   /api/v1/swiss-matches        # Create Swiss match
GET    /api/v1/swiss-matches        # List Swiss matches
PUT    /api/v1/swiss-matches/{id}   # Update Swiss match
POST   /api/v1/elimination-matches  # Create elimination match
GET    /api/v1/elimination-matches  # List elimination matches
PUT    /api/v1/elimination-matches/{id} # Update elimination match
```

#### Arena Integration
```http
POST   /api/v1/arena/start-match    # Start match on arena
POST   /api/v1/arena/complete-match # Complete match
GET    /api/v1/arena/status         # Get arena status
POST   /api/v1/arena/configure-hazards # Configure hazards
POST   /api/v1/arena/reset          # Reset arena
```

#### Public Display
```http
GET    /api/v1/public/current-match # Get current match
GET    /api/v1/public/upcoming-matches # Get upcoming matches
GET    /api/v1/public/standings     # Get standings
GET    /api/v1/public/brackets      # Get brackets
```

#### WebSocket Endpoints
```http
WS     /ws/tournament-updates       # Real-time tournament updates
WS     /ws/arena-status             # Real-time arena status
WS     /ws/user-presence            # User presence updates
```

### Data Models

#### Tournament
```python
{
    "id": 1,
    "name": "NRC Spring Tournament 2024",
    "format": "hybrid_swiss_elimination",
    "status": "setup",
    "swiss_rounds": 3,
    "location": "NRC Arena",
    "description": "Spring robotics tournament",
    "start_date": "2024-03-15T09:00:00Z",
    "end_date": "2024-03-15T18:00:00Z",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
}
```

#### Robot Class
```python
{
    "id": 1,
    "name": "150g - Non-Destructive",
    "weight_limit": 150,
    "match_duration": 120,
    "pit_activation_time": 60,
    "button_delay": null,
    "button_duration": null,
    "description": "Antweight non-destructive class",
    "created_at": "2024-01-15T10:00:00Z"
}
```

#### Team
```python
{
    "id": 1,
    "tournament_id": 1,
    "name": "Quokka Riot!",
    "address": "Sunshine Coast, QLD",
    "phone": "0422745355",
    "email": "noosarobotics@gmail.com",
    "created_at": "2024-01-15T10:00:00Z"
}
```

## Database Schema

### Core Tables
- `tournaments`: Tournament information and configuration
- `robot_classes`: Robot class definitions and timing
- `teams`: Team registration information
- `robots`: Individual robot entries
- `players`: Team member information

### Tournament Progression
- `swiss_rounds`: Swiss round configuration
- `swiss_matches`: Swiss round match results
- `elimination_brackets`: Elimination bracket structure
- `elimination_matches`: Elimination match results

### Arena Integration
- `arena_events`: Arena communication logs
- `hazard_configs`: Hazard timing configuration

### Multi-User Access
- `user_sessions`: User session management
- `concurrent_operations`: Concurrent access tracking

### Data Import
- `csv_imports`: CSV import history and logs

## Development

### Project Structure
```
backend/
├── models.py              # Database models
├── schemas.py             # Pydantic schemas
├── database.py            # Database configuration
├── config.py              # Settings management
├── main.py               # FastAPI application
├── arena_integration.py   # Arena communication
├── csv_import.py          # CSV import handling
├── services/              # Business logic services
│   ├── __init__.py
│   ├── container.py       # Dependency injection
│   ├── tournament_service.py
│   ├── validation_service.py
│   └── ...
├── tests/                 # Test suite
│   ├── conftest.py        # Test configuration
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── pytest.ini           # Test configuration
├── .pre-commit-config.yaml # Code quality hooks
├── env.example           # Environment template
├── venv/                 # Virtual environment (created)
└── README.md             # This file
```

### Running Tests
```bash
# Make sure environment is activated
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests only
pytest tests/e2e/         # End-to-end tests only
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Development Server
```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Deployment

### Single Pi Deployment
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv

# Set up application
cd /opt/nrc-tournament
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure service
sudo cp nrc-tournament.service /etc/systemd/system/
sudo systemctl enable nrc-tournament
sudo systemctl start nrc-tournament
```

### Cross-Platform Deployment
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Configuration

### Platform Detection
The system automatically detects the platform and optimizes settings:
- **Raspberry Pi**: Reduced pool sizes, SQLite database, slower refresh rates
- **Desktop/Laptop**: Full performance settings, PostgreSQL support
- **Development**: Debug mode, auto-reload, detailed logging

### Database Configuration
- **SQLite**: Default for development and simple deployment
- **PostgreSQL**: Recommended for production and large tournaments
- **Automatic Setup**: Database tables and default robot classes created automatically

### Arena Integration
- **REST API**: HTTP communication with arena system
- **WebSocket**: Real-time status updates
- **Error Handling**: Graceful degradation when arena unavailable
- **Configuration**: Arena URL and API key in environment variables

## Troubleshooting

### Common Issues

#### Virtual Environment Issues
```bash
# If you see global packages, you're not in the virtual environment
pip list | grep -v venv  # Should show only project packages

# Recreate environment if corrupted
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Database Connection Errors
```bash
# Check database URL
echo $DATABASE_URL

# Test connection
python -c "from database import test_database_connection; print(test_database_connection())"

# Reset database
rm nrc_tournament.db
python -c "from database import create_db_and_tables; create_db_and_tables()"
```

#### Arena Integration Issues
```bash
# Check arena system status
curl http://localhost:8001/api/v1/arena/status

# Test arena communication
python -c "from arena_integration import ArenaIntegration; import asyncio; print(asyncio.run(ArenaIntegration().get_status()))"
```

#### Performance Issues
```bash
# Check memory usage
ps aux | grep uvicorn

# Monitor database performance
python -c "from database import get_database_info; print(get_database_info())"
```

### Logging
```python
# Configure logging level
import logging
logging.basicConfig(level=logging.DEBUG)

# View application logs
tail -f logs/tournament.log
```

## Contributing

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all functions
- Add docstrings for all classes and methods
- Write tests for new features

### Testing
- Unit tests for all modules
- Integration tests for API endpoints
- Performance tests for database operations
- Hardware tests for arena integration

### Documentation
- Update API documentation for new endpoints
- Add examples for new features
- Update deployment instructions
- Maintain development log

## License
AGPL-3.0 License - See LICENSE file for details

## Support
For issues and questions:
1. Check the troubleshooting section
2. Review the development log
3. Check the design documents
4. Create an issue in the repository
