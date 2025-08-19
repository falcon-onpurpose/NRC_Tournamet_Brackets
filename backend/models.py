"""
Data models for NRC Tournament Program
"""

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class TournamentFormat(str, Enum):
    HYBRID_SWISS_ELIMINATION = "hybrid_swiss_elimination"
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    SWISS = "swiss"
    ROUND_ROBIN = "round_robin"

class TournamentStatus(str, Enum):
    SETUP = "setup"
    REGISTRATION = "registration"
    SWISS_ROUNDS = "swiss_rounds"
    ELIMINATION = "elimination"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"

class ArenaState(str, Enum):
    IDLE = "idle"
    TEAMS_READY = "teams_ready"
    INTRO_COUNTDOWN = "intro_countdown"
    MAIN_PROGRAM = "main_program"
    HAZARD_ACTIVE = "hazard_active"
    MATCH_COMPLETE = "match_complete"
    PAUSED = "paused"
    ERROR = "error"

# Base Models
class TournamentBase(SQLModel):
    name: str = Field(index=True)
    format: str = Field(default="hybrid_swiss_elimination")
    status: str = Field(default="setup")
    swiss_rounds: int = Field(default=3)
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class RobotClassBase(SQLModel):
    name: str = Field(index=True)
    weight_limit: int = Field(description="Weight limit in grams")
    match_duration: int = Field(description="Match duration in seconds")
    pit_activation_time: int = Field(description="Seconds remaining when pit activates")
    button_delay: Optional[int] = Field(default=None, description="Seconds after match start when button becomes active")
    button_duration: Optional[int] = Field(default=None, description="Seconds button remains active")
    description: Optional[str] = None

class TeamBase(SQLModel):
    name: str = Field(index=True)
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class RobotBase(SQLModel):
    name: str = Field(index=True)
    robot_class_id: int = Field(foreign_key="robotclass.id")
    waitlist: bool = Field(default=False)
    fee_paid: bool = Field(default=False)
    comments: Optional[str] = None

class PlayerBase(SQLModel):
    first_name: str
    last_name: str
    email: Optional[str] = None

# Database Models
class Tournament(TournamentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    teams: List["Team"] = Relationship(back_populates="tournament")
    robot_classes: List["TournamentRobotClass"] = Relationship(back_populates="tournament")
    swiss_rounds: List["SwissRound"] = Relationship(back_populates="tournament")
    elimination_brackets: List["EliminationBracket"] = Relationship(back_populates="tournament")
    arena_events: List["ArenaEvent"] = Relationship(back_populates="tournament")

class RobotClass(RobotClassBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    robots: List["Robot"] = Relationship(back_populates="robot_class")
    tournament_classes: List["TournamentRobotClass"] = Relationship(back_populates="robot_class")

class TournamentRobotClass(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id")
    robot_class_id: int = Field(foreign_key="robotclass.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    tournament: Tournament = Relationship(back_populates="robot_classes")
    robot_class: RobotClass = Relationship(back_populates="tournament_classes")

class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    tournament: Tournament = Relationship(back_populates="teams")
    robots: List["Robot"] = Relationship(back_populates="team")
    players: List["Player"] = Relationship(back_populates="team")

class Robot(RobotBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="team.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    team: Team = Relationship(back_populates="robots")
    robot_class: RobotClass = Relationship(back_populates="robots")

class Player(PlayerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="team.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    team: Team = Relationship(back_populates="players")

# Tournament Progression Models
class SwissRound(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id")
    robot_class_id: int = Field(foreign_key="robotclass.id")
    round_number: int = Field(default=1)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    tournament: Tournament = Relationship(back_populates="swiss_rounds")
    matches: List["SwissMatch"] = Relationship(back_populates="swiss_round")

class SwissMatch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    swiss_round_id: int = Field(foreign_key="swissround.id")
    team1_id: int = Field(foreign_key="team.id")
    team2_id: int = Field(foreign_key="team.id")
    winner_id: Optional[int] = Field(default=None, foreign_key="team.id")
    # Use builtin dict to avoid typing.Dict issues with SQLModel type detection
    scores: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    status: str = Field(default="scheduled")
    scheduled_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    swiss_round: "SwissRound" = Relationship(back_populates="matches")
    team1: "Team" = Relationship(sa_relationship_kwargs={"foreign_keys": "SwissMatch.team1_id"})
    team2: "Team" = Relationship(sa_relationship_kwargs={"foreign_keys": "SwissMatch.team2_id"})
    winner: Optional["Team"] = Relationship(sa_relationship_kwargs={"foreign_keys": "SwissMatch.winner_id"})

class EliminationBracket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id")
    robot_class_id: int = Field(foreign_key="robotclass.id")
    bracket_type: str = Field(description="winners or losers")
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    tournament: Tournament = Relationship(back_populates="elimination_brackets")
    matches: List["EliminationMatch"] = Relationship(back_populates="bracket")

class EliminationMatch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bracket_id: int = Field(foreign_key="eliminationbracket.id")
    team1_id: int = Field(foreign_key="team.id")
    team2_id: int = Field(foreign_key="team.id")
    winner_id: Optional[int] = Field(default=None, foreign_key="team.id")
    scores: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    status: str = Field(default="scheduled")
    scheduled_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    round_number: int = Field(default=1)
    match_number: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    bracket: EliminationBracket = Relationship(back_populates="matches")
    team1: Team = Relationship(sa_relationship_kwargs={"foreign_keys": "EliminationMatch.team1_id"})
    team2: Team = Relationship(sa_relationship_kwargs={"foreign_keys": "EliminationMatch.team2_id"})
    winner: Optional[Team] = Relationship(sa_relationship_kwargs={"foreign_keys": "EliminationMatch.winner_id"})

# Arena Integration Models
class ArenaEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id")
    match_id: Optional[int] = Field(default=None)
    event_type: str = Field(description="start_match, complete_match, hazard_activation, etc.")
    data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    tournament: Tournament = Relationship(back_populates="arena_events")

class HazardConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(description="Swiss or Elimination match ID")
    match_type: str = Field(description="swiss or elimination")
    pit_activation_time: int = Field(description="Seconds remaining when pit activates")
    button_delay: Optional[int] = Field(default=None)
    button_duration: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Multi-User Access Models
class UserSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(description="Simple username for organizers")
    session_token: str = Field(unique=True, index=True)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConcurrentOperation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(description="Username of user performing operation")
    operation_type: str = Field(description="Type of operation performed")
    data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# CSV Import Models
class CSVImport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id")
    filename: str
    import_status: str = Field(default="pending")
    records_processed: int = Field(default=0)
    records_successful: int = Field(default=0)
    records_failed: int = Field(default=0)
    error_log: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
