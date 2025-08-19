# NRC Tournament Program

A tournament management system based on the Bracket tournament system, enhanced with arena integration and public display capabilities.

## Features

- **Tournament Formats**: Single elimination, double elimination, swiss, round robin
- **Web Interface**: Modern Next.js frontend for tournament management
- **Public Displays**: View-only interfaces for waiting areas and arena displays
- **Arena Integration**: Real-time communication with arena control system
- **Match Coordination**: Automatic pit assignments and timing synchronization

## Architecture

### Backend (FastAPI)
- Tournament bracket management
- Match scheduling and coordination
- Arena system integration
- REST API for frontend and arena communication

### Frontend (Next.js)
- Tournament management interface
- Real-time bracket visualization
- Public display views
- Responsive design for various screen sizes

### Arena Integration
- Match parameter communication
- Real-time status updates
- Score and winner reporting

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL
- UV or pyenv for Python environment management

### Development Setup

1. **Backend Setup**
```bash
cd "NRC Tournament Program/backend"
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt
```

2. **Frontend Setup**
```bash
cd "NRC Tournament Program/frontend"
npm install
```

3. **Database Setup**
```bash
# Start PostgreSQL
# Create database and run migrations
```

4. **Run Development Servers**
```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

## Configuration

- Backend configuration via environment variables or `.env` files
- Frontend configuration via Next.js environment variables
- Arena integration settings in `arena_integration/config.py`

## Deployment

### Single Raspberry Pi Deployment
Both tournament and arena systems can run on a single Raspberry Pi 3B+ with:
- Lightweight FastAPI backend
- Optimized Next.js frontend
- Efficient database usage
- GPIO control for arena hardware

### Multi-System Deployment
For larger tournaments, systems can be deployed separately:
- Tournament system on dedicated server
- Arena system on Raspberry Pi
- Network communication between systems

## API Documentation

- Backend API: `http://localhost:8000/docs`
- Arena Integration API: `http://localhost:8000/arena/docs`

## License

Based on Bracket tournament system (AGPL-3.0)
