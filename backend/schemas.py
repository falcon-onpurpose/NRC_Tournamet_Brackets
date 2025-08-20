"""
Pydantic schemas for NRC Tournament Program API
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import TournamentFormat, TournamentStatus, MatchStatus, ArenaState

# Base Schemas
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None

# Tournament Schemas
class TournamentCreate(BaseModel):
    name: str = Field(..., max_length=100)
    format: str = Field(default=TournamentFormat.HYBRID_SWISS_ELIMINATION.value)
    swiss_rounds_count: int = Field(default=3)
    max_teams: int = Field(default=16, gt=0, le=100)
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = Field(default=TournamentStatus.SETUP.value)

class TournamentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    format: Optional[str] = None
    swiss_rounds_count: Optional[int] = Field(None)
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[TournamentStatus] = None

class TournamentResponse(TournamentCreate):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    team_count: int = 0
    robot_class_count: int = 0
    
    model_config = {"from_attributes": True}

# Robot Class Schemas
class RobotClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    weight_limit: int = Field(..., gt=0, le=10000)
    match_duration: int = Field(..., gt=0, le=3600)
    pit_activation_time: int = Field(..., ge=0, le=3600)
    button_delay: Optional[int] = Field(None, ge=0, le=3600)
    button_duration: Optional[int] = Field(None, gt=0, le=3600)
    description: Optional[str] = None

    @field_validator('pit_activation_time')
    @classmethod
    def pit_activation_must_be_less_than_duration(cls, v, info):
        if info.data and 'match_duration' in info.data and v >= info.data['match_duration']:
            raise ValueError('Pit activation time must be less than match duration')
        return v

    @field_validator('button_delay')
    @classmethod
    def button_delay_must_be_less_than_duration(cls, v, info):
        if v is not None and info.data and 'match_duration' in info.data and v >= info.data['match_duration']:
            raise ValueError('Button delay must be less than match duration')
        return v

class RobotClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    weight_limit: Optional[int] = Field(None, gt=0, le=10000)
    match_duration: Optional[int] = Field(None, gt=0, le=3600)
    pit_activation_time: Optional[int] = Field(None, ge=0, le=3600)
    button_delay: Optional[int] = Field(None, ge=0, le=3600)
    button_duration: Optional[int] = Field(None, gt=0, le=3600)
    description: Optional[str] = None

class RobotClassResponse(RobotClassCreate):
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

# Team Schemas
class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    tournament_id: int = Field(..., description="Tournament ID that this team belongs to")
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class TeamResponse(TeamCreate):
    id: int
    tournament_id: int
    created_at: datetime
    robot_count: int = 0
    player_count: int = 0
    
    model_config = {"from_attributes": True}

# Robot Schemas
class RobotCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    robot_class_id: int
    waitlist: bool = False
    fee_paid: bool = False
    comments: Optional[str] = None

class RobotUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    robot_class_id: Optional[int] = None
    waitlist: Optional[bool] = None
    fee_paid: Optional[bool] = None
    comments: Optional[str] = None

class RobotResponse(RobotCreate):
    id: int
    team_id: int
    created_at: datetime
    robot_class_name: str
    
    model_config = {"from_attributes": True}

# Player Schemas
class PlayerCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = None

class PlayerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = None

class PlayerResponse(PlayerCreate):
    id: int
    team_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

# Match Schemas
class MatchBase(BaseModel):
    tournament_id: Optional[int] = None
    round_number: Optional[int] = None
    team1_id: int
    team2_id: int
    scheduled_time: Optional[datetime] = None

class SwissMatchCreate(MatchBase):
    swiss_round_id: Optional[int] = None

class SwissMatchUpdate(BaseModel):
    winner_id: Optional[int] = None
    scores: Optional[Dict[str, Any]] = None
    status: Optional[MatchStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class SwissMatchResponse(SwissMatchCreate):
    id: int
    winner_id: Optional[int] = None
    scores: Optional[Dict[str, Any]] = None
    status: MatchStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    team1_name: str
    team2_name: str
    winner_name: Optional[str] = None
    
    model_config = {"from_attributes": True}

class EliminationMatchCreate(MatchBase):
    bracket_id: int
    round_number: int = 1
    match_number: int = 1

class EliminationMatchUpdate(BaseModel):
    winner_id: Optional[int] = None
    scores: Optional[Dict[str, Any]] = None
    status: Optional[MatchStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class EliminationMatchResponse(EliminationMatchCreate):
    id: int
    winner_id: Optional[int] = None
    scores: Optional[Dict[str, Any]] = None
    status: MatchStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    team1_name: str
    team2_name: str
    winner_name: Optional[str] = None
    
    model_config = {"from_attributes": True}

# Match Result Schemas
class MatchResultCreate(BaseModel):
    winner_id: int
    team1_score: int = Field(..., ge=0)
    team2_score: int = Field(..., ge=0)
    completion_reason: Optional[str] = Field(None, pattern=r"^(timeout|reset|manual|forfeit)$")
    notes: Optional[str] = None

# Arena Integration Schemas
class ArenaMatchStart(BaseModel):
    match_id: int
    match_type: str = Field(..., pattern=r"^(swiss|elimination)$")
    duration: int = Field(..., ge=60, le=3600)
    pit_activation_time: int = Field(..., ge=0, le=3600)
    button_delay: Optional[int] = Field(None, ge=0, le=3600)
    button_duration: Optional[int] = Field(None, gt=0, le=3600)
    team1_name: str
    team2_name: str

class ArenaMatchComplete(BaseModel):
    match_id: int
    match_type: str = Field(..., pattern=r"^(swiss|elimination)$")
    winner_id: Optional[int] = None
    scores: Optional[Dict[str, Any]] = None
    completion_reason: str = Field(..., pattern=r"^(timeout|reset|manual)$")

class ArenaStatus(BaseModel):
    state: ArenaState
    current_match: Optional[Dict[str, Any]] = None
    time_remaining: Optional[int] = None
    hazard_status: Optional[Dict[str, Any]] = None
    hardware_status: Optional[Dict[str, Any]] = None
    last_update: datetime = Field(default_factory=datetime.utcnow)

class HazardConfig(BaseModel):
    pit_activation_time: int = Field(..., ge=0, le=3600)
    button_delay: Optional[int] = Field(None, ge=0, le=3600)
    button_duration: Optional[int] = Field(None, gt=0, le=3600)

# CSV Import Schemas
class CSVImportRequest(BaseModel):
    tournament_id: int
    csv_data: str  # Base64 encoded CSV content
    filename: str

class CSVImportResponse(BaseModel):
    import_id: int
    status: str
    records_processed: int
    records_successful: int
    records_failed: int
    error_log: Optional[Dict[str, Any]] = None
    created_at: datetime

# Public Display Schemas
class PublicMatchInfo(BaseModel):
    match_id: int
    match_type: str
    team1_name: str
    team2_name: str
    status: MatchStatus
    time_remaining: Optional[int] = None
    scheduled_time: Optional[datetime] = None
    robot_class: str

class PublicTournamentInfo(BaseModel):
    tournament_id: int
    name: str
    status: TournamentStatus
    current_phase: str
    active_classes: List[str]
    total_teams: int
    total_matches: int
    completed_matches: int

class PublicStandings(BaseModel):
    robot_class: str
    standings: List[Dict[str, Any]]
    last_updated: datetime

# Multi-User Access Schemas
class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)

class UserSession(BaseModel):
    session_token: str
    user_id: str
    created_at: datetime
    last_activity: datetime

class ConcurrentOperation(BaseModel):
    operation_type: str
    data: Dict[str, Any]
    timestamp: datetime
    user_id: str

# WebSocket Schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UserPresence(BaseModel):
    user_id: str
    active: bool
    last_activity: datetime
    current_action: Optional[str] = None

# Error Response Schemas
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Success Response Schemas
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# List Response Schemas
class TournamentListResponse(BaseModel):
    tournaments: List[TournamentResponse]
    total: int
    page: int
    per_page: int

class TeamListResponse(BaseModel):
    teams: List[TeamResponse]
    total: int
    page: int
    per_page: int

class RobotListResponse(BaseModel):
    robots: List[RobotResponse]
    total: int
    page: int
    per_page: int

class MatchListResponse(BaseModel):
    matches: List[SwissMatchResponse]
    total: int
    page: int
    per_page: int

class MatchStatisticsResponse(BaseModel):
    swiss_matches: Dict[str, int]
    elimination_matches: Dict[str, int]

# Team Registration and Import Schemas
class TeamRegistrationResponse(BaseModel):
    team: TeamResponse
    robots: List[RobotResponse]
    players: List[PlayerResponse]
    registration_time: datetime = Field(default_factory=datetime.utcnow)

class TeamImportResponse(BaseModel):
    imported_count: int
    error_count: int
    teams: List[TeamResponse]
    errors: List[Dict[str, Any]]
    import_report: Optional[str] = None
    validation_summary: Optional[Dict[str, Any]] = None
