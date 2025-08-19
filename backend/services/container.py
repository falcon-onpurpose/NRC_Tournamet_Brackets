"""
Dependency injection container for NRC Tournament Program services.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from database import get_session
from .tournament_service import TournamentService
from .match_service import MatchService

from .team_service import TeamService

from .bracket_service import BracketService
from .standings_service import StandingsService
from .validation_service import ValidationService


class Container:
    """
    Dependency injection container for all services.
    Manages service lifecycle and dependencies.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._tournament_service: Optional[TournamentService] = None
        self._match_service: Optional[MatchService] = None
        self._team_service: Optional[TeamService] = None
        self._bracket_service: Optional[BracketService] = None
        self._standings_service: Optional[StandingsService] = None
        self._validation_service: Optional[ValidationService] = None
    
    @property
    def tournament_service(self) -> TournamentService:
        """Get tournament service instance."""
        if self._tournament_service is None:
            self._tournament_service = TournamentService(self.settings)
        return self._tournament_service
    
    @property
    def match_service(self) -> MatchService:
        """Get match service instance."""
        if self._match_service is None:
            self._match_service = MatchService(self.settings)
        return self._match_service
    
    @property
    def team_service(self) -> TeamService:
        """Get team service instance."""
        if self._team_service is None:
            self._team_service = TeamService(self.settings)
        return self._team_service
    
    @property
    def bracket_service(self) -> BracketService:
        """Get bracket service instance."""
        if self._bracket_service is None:
            self._bracket_service = BracketService()
        return self._bracket_service
    
    @property
    def standings_service(self) -> StandingsService:
        """Get standings service instance."""
        if self._standings_service is None:
            self._standings_service = StandingsService()
        return self._standings_service
    
    @property
    def validation_service(self) -> ValidationService:
        """Get validation service instance."""
        if self._validation_service is None:
            self._validation_service = ValidationService()
        return self._validation_service
    
    def get_tournament_service_with_session(self, session: AsyncSession) -> TournamentService:
        """Get tournament service with specific database session."""
        return TournamentService(self.settings, session)
    
    def get_match_service_with_session(self, session: AsyncSession) -> MatchService:
        """Get match service with specific database session."""
        return MatchService(self.settings)
    
    def get_team_service_with_session(self, session: AsyncSession) -> TeamService:
        """Get team service with specific database session."""
        return TeamService(self.settings)
    
    def get_bracket_service_with_session(self, session: AsyncSession) -> BracketService:
        """Get bracket service with specific database session."""
        return BracketService(session)
    
    def get_standings_service_with_session(self, session: AsyncSession) -> StandingsService:
        """Get standings service with specific database session."""
        return StandingsService(session)


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container instance."""
    global _container
    if _container is None:
        from config import get_settings
        _container = Container(get_settings())
    return _container


def reset_container():
    """Reset the global container instance (for testing)."""
    global _container
    _container = None
