# NRC Tournament Program - Technical Design Document

## 1. System Overview

### 1.1 Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Tournament    │    │     Arena       │    │   Public        │
│   Management    │◄──►│   Control       │◄──►│   Displays      │
│   System        │    │   System        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   Hardware      │    │   Network       │
│   (PostgreSQL/  │    │   (GPIO/LEDs)   │    │   (Local/WiFi)  │
│    SQLite)      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.2 Technology Stack
- **Backend**: Python 3.8+ with FastAPI
- **Frontend**: Next.js 18+ with TypeScript
- **Database**: PostgreSQL (production) / SQLite (development)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Real-time**: WebSocket connections
- **Deployment**: Cross-platform (Windows, macOS, Linux, Raspberry Pi)

## 2. Core Components

### 2.1 Tournament Management System
- **Tournament Creation**: Hybrid Swiss + Double Elimination format
- **Robot Class Management**: Antweight, Beetleweight with class-specific timing
- **Team Registration**: CSV import from robotcombatevents.com
- **Match Scheduling**: Multi-class rotation with arena coordination
- **Results Management**: Real-time scoring and bracket progression

### 2.2 Arena Integration System
- **Communication Protocol**: REST API + WebSocket for real-time updates
- **Match Coordination**: Start/stop matches, hazard configuration
- **Status Monitoring**: Arena availability, hardware status
- **Error Handling**: Graceful degradation when arena unavailable

### 2.3 Multi-User Concurrent Access
- **Real-time Collaboration**: WebSocket-based synchronization
- **Conflict Resolution**: Optimistic locking with conflict detection
- **User Presence**: Active user indicators and activity tracking
- **Audit Trails**: Complete operation logging

## 3. Database Design

### 3.1 Core Tables
```sql
-- Tournament Management
tournaments (id, name, format, status, created_at, updated_at)
robot_classes (id, name, weight_limit, match_duration, pit_activation_time)
teams (id, name, address, phone, email, created_at)
robots (id, team_id, name, robot_class_id, waitlist, fee_paid)
players (id, team_id, first_name, last_name, email)

-- Tournament Progression
swiss_rounds (id, tournament_id, class_id, round_number, status)
swiss_matches (id, swiss_round_id, team1_id, team2_id, winner_id, scores)
elimination_brackets (id, tournament_id, class_id, bracket_type, status)
elimination_matches (id, bracket_id, team1_id, team2_id, winner_id, scores)

-- Arena Integration
arena_events (id, tournament_id, match_id, event_type, data, timestamp)
hazard_configs (id, match_id, pit_activation_time, button_delay, duration)

-- Multi-User Access
user_sessions (id, user_id, session_token, last_activity, created_at)
concurrent_operations (id, user_id, operation_type, data, timestamp)
```

### 3.2 Relationships
- **Tournament → Robot Classes**: Many-to-many through tournament_classes
- **Team → Robots**: One-to-many (teams can have multiple robots)
- **Robot → Robot Class**: Many-to-one (each robot belongs to one class)
- **Tournament → Matches**: One-to-many through Swiss and elimination rounds

## 4. API Design

### 4.1 Tournament Management APIs
```python
# Tournament CRUD
POST   /api/v1/tournaments
GET    /api/v1/tournaments
GET    /api/v1/tournaments/{id}
PUT    /api/v1/tournaments/{id}
DELETE /api/v1/tournaments/{id}

# Robot Class Management
POST   /api/v1/robot-classes
GET    /api/v1/robot-classes
PUT    /api/v1/robot-classes/{id}

# Team Registration
POST   /api/v1/teams/import-csv
POST   /api/v1/teams
GET    /api/v1/teams
PUT    /api/v1/teams/{id}

# Match Management
POST   /api/v1/matches/start
POST   /api/v1/matches/{id}/complete
PUT    /api/v1/matches/{id}/delay
GET    /api/v1/matches/schedule
```

### 4.2 Arena Integration APIs
```python
# Arena Communication
POST   /api/v1/arena/start-match
POST   /api/v1/arena/complete-match
GET    /api/v1/arena/status
POST   /api/v1/arena/configure-hazards
POST   /api/v1/arena/reset

# Real-time Updates
WS     /ws/tournament-updates
WS     /ws/arena-status
WS     /ws/user-presence
```

### 4.3 Public Display APIs
```python
# Read-only tournament data
GET    /api/v1/public/current-match
GET    /api/v1/public/upcoming-matches
GET    /api/v1/public/standings
GET    /api/v1/public/brackets
```

## 5. Frontend Architecture

### 5.1 Component Structure
```
src/
├── components/
│   ├── tournament/
│   │   ├── TournamentManager.tsx
│   │   ├── RobotClassManager.tsx
│   │   ├── TeamRegistration.tsx
│   │   ├── MatchScheduler.tsx
│   │   └── ResultsManager.tsx
│   ├── arena/
│   │   ├── ArenaStatus.tsx
│   │   ├── HazardConfig.tsx
│   │   └── MatchControl.tsx
│   ├── public/
│   │   ├── CurrentMatch.tsx
│   │   ├── UpcomingMatches.tsx
│   │   ├── Standings.tsx
│   │   └── Brackets.tsx
│   └── shared/
│       ├── Layout.tsx
│       ├── Navigation.tsx
│       └── UserPresence.tsx
├── pages/
│   ├── tournament/
│   ├── arena/
│   ├── public/
│   └── admin/
└── hooks/
    ├── useTournament.ts
    ├── useArena.ts
    ├── useWebSocket.ts
    └── useConcurrentAccess.ts
```

### 5.2 State Management
- **React Context**: For global tournament state
- **WebSocket Hooks**: For real-time updates
- **Optimistic Updates**: For immediate UI feedback
- **Conflict Resolution**: For concurrent access handling

## 6. Deployment Architecture

### 6.1 Single Pi Deployment
```
Raspberry Pi 3B+
├── Tournament System (FastAPI + Next.js)
├── Arena System (Python + GPIO)
├── PostgreSQL Database
└── Web Interface (Port 3000)
```

### 6.2 Dual Pi Deployment
```
Pi 1 (Tournament)
├── Tournament System (FastAPI + Next.js)
├── PostgreSQL Database
└── Web Interface (Port 3000)

Pi 2 (Arena)
├── Arena System (Python + GPIO)
└── Arena API (Port 8001)
```

### 6.3 Cross-Platform Deployment
```
Desktop/Laptop
├── Tournament System (FastAPI + Next.js)
├── SQLite Database
└── Web Interface (Port 3000)

Raspberry Pi (Arena)
├── Arena System (Python + GPIO)
└── Arena API (Port 8001)
```

## 7. Security & Access Control

### 7.1 Authentication
- **Session-based**: Simple username/password for organizers
- **No authentication**: Read-only access for spectators
- **API Keys**: For arena system communication

### 7.2 Authorization
- **Full Access**: Tournament organizers and referees
- **Read-only**: Spectators and participants
- **Arena Access**: Arena system API communication

### 7.3 Data Protection
- **Local network only**: No remote access
- **Audit trails**: All operations logged
- **Data validation**: Input sanitization and validation

## 8. Performance Considerations

### 8.1 Scalability Targets
- **Tournaments**: Up to 64 teams
- **Concurrent Users**: 10 full-access, 50 read-only
- **Real-time Updates**: Sub-second synchronization
- **Database**: Optimized for Raspberry Pi performance

### 8.2 Resource Optimization
- **Memory**: Efficient data structures and caching
- **CPU**: Async operations and background tasks
- **Storage**: Compressed tournament archives
- **Network**: Minimal WebSocket traffic

## 9. Testing Strategy

### 9.1 Unit Testing
- **Backend**: Pytest for API endpoints and business logic
- **Frontend**: Jest + React Testing Library
- **Database**: SQLModel test fixtures

### 9.2 Integration Testing
- **Arena Communication**: Mock arena system
- **Multi-user Access**: Concurrent user simulation
- **CSV Import**: Sample data validation

### 9.3 Performance Testing
- **Load Testing**: Multiple concurrent users
- **Memory Testing**: Long-running tournament simulation
- **Network Testing**: Arena communication reliability

## 10. Development Phases

### Phase 1: Core Tournament System (Week 1-2)
- [ ] Database schema implementation
- [ ] Basic tournament CRUD operations
- [ ] Robot class management
- [ ] Team registration (manual entry)

### Phase 2: Arena Integration (Week 3)
- [ ] Arena communication API
- [ ] Match coordination system
- [ ] Hazard configuration
- [ ] Real-time status updates

### Phase 3: Advanced Features (Week 4-5)
- [ ] CSV import functionality
- [ ] Multi-class tournament management
- [ ] Swiss + elimination hybrid format
- [ ] Multi-user concurrent access

### Phase 4: Frontend & UI (Week 6-7)
- [ ] Tournament management interface
- [ ] Public display views
- [ ] Real-time collaboration features
- [ ] Mobile-responsive design

### Phase 5: Testing & Deployment (Week 8)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Deployment documentation
- [ ] User guides and training

---

**Document Version**: 1.0  
**Last Updated**: [Current Date]  
**Next Review**: [Date + 7 days]
