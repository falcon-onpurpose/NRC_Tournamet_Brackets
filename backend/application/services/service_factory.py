"""
Service factory for dependency injection.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from domain.team.team_repository import TeamRepository
from domain.team.team_service import TeamService
from domain.team.team_validator import TeamValidator
from domain.match.match_repository import MatchRepository
from domain.match.match_service import MatchService
from domain.match.match_validator import MatchValidator
from domain.validation.validation_service import ValidationService
from domain.csv_import.import_orchestrator import ImportOrchestrator
from domain.robot.robot_repository import RobotRepository
from domain.robot.robot_service import RobotService
from domain.robot.robot_validator import RobotValidator
from domain.player.player_repository import PlayerRepository
from domain.player.player_service import PlayerService
from domain.player.player_validator import PlayerValidator
from domain.robot_class.robot_class_repository import RobotClassRepository
from domain.robot_class.robot_class_service import RobotClassService
from domain.robot_class.robot_class_validator import RobotClassValidator


class ServiceFactory:
    """Factory for creating services with proper dependencies."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def create_team_service(self) -> TeamService:
        """Create team service with dependencies."""
        repository = TeamRepository(self.session)
        validator = TeamValidator()
        return TeamService(repository, validator)
    
    def create_match_service(self) -> MatchService:
        """Create match service with dependencies."""
        repository = MatchRepository(self.session)
        validator = MatchValidator()
        return MatchService(repository, validator)
    
    def create_validation_service(self) -> ValidationService:
        """Create validation service with dependencies."""
        return ValidationService()
    
    def create_csv_import_service(self) -> ImportOrchestrator:
        """Create CSV import service with dependencies."""
        validation_service = self.create_validation_service()
        return ImportOrchestrator(validation_service)
    
    def create_robot_service(self) -> RobotService:
        """Create robot service with dependencies."""
        repository = RobotRepository(self.session)
        validator = RobotValidator(repository)
        return RobotService(repository, validator)
    
    def create_player_service(self) -> PlayerService:
        """Create player service with dependencies."""
        repository = PlayerRepository(self.session)
        validator = PlayerValidator(repository)
        return PlayerService(repository, validator)
    
    def create_robot_class_service(self) -> RobotClassService:
        """Create robot class service with dependencies."""
        repository = RobotClassRepository(self.session)
        validator = RobotClassValidator(repository)
        return RobotClassService(repository, validator)
