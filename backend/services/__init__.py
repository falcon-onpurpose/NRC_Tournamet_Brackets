"""
Services package for NRC Tournament Program.
Provides business logic layer with dependency injection.
"""

from .container import Container
from .tournament_service import TournamentService
from .match_service import MatchService

try:
    from .team_service import TeamService  # type: ignore
except Exception:
    TeamService = None  # type: ignore

try:
    from .bracket_service import BracketService  # type: ignore
except Exception:
    BracketService = None  # type: ignore

try:
    from .standings_service import StandingsService  # type: ignore
except Exception:
    StandingsService = None  # type: ignore
from .validation_service import ValidationService

__all__ = [
    "Container",
    "TournamentService",
    "MatchService", 
    "TeamService",
    "BracketService",
    "StandingsService",
    "ValidationService",
]
