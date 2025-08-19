"""
Team service for business logic operations.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from domain.shared.repository import BaseService
from domain.team.team_repository import TeamRepository
from domain.team.team_validator import TeamValidator
from models import Team, Robot, Player, RobotClass
from schemas import TeamCreate, TeamUpdate, TeamResponse, RobotCreate, RobotUpdate, RobotResponse, PlayerCreate, PlayerUpdate, PlayerResponse, RobotClassCreate, RobotClassUpdate, RobotClassResponse


class TeamService(BaseService):
    """Service for team-related business logic."""
    
    def __init__(self, repository: TeamRepository, validator: TeamValidator):
        super().__init__(repository)
        self.validator = validator
    
    # Team Management Methods
    async def create_team(self, team_data: TeamCreate) -> TeamResponse:
        """Create a new team."""
        # Validate team data
        validation_result = self.validator.validate_team_data(team_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid team data: {validation_result.errors}")
        
        # Check for duplicate team name
        if await self.repository.exists_by_name(team_data.name):
            raise ValueError(f"Team with name '{team_data.name}' already exists")
        
        # Create team
        team = Team(
            name=team_data.name,
            address=team_data.address,
            phone=team_data.phone,
            email=team_data.email,
            tournament_id=team_data.tournament_id
        )
        
        saved_team = await self.repository.save(team)
        return TeamResponse.model_validate(saved_team)
    
    async def get_team(self, team_id: int) -> Optional[TeamResponse]:
        """Get team by ID."""
        team = await self.repository.find_by_id(team_id)
        if not team:
            return None
        
        return TeamResponse.model_validate(team)
    
    async def get_teams(self, **filters) -> List[TeamResponse]:
        """Get teams with optional filters."""
        teams = await self.repository.find_all(**filters)
        return [TeamResponse.model_validate(team) for team in teams]
    
    async def update_team(self, team_id: int, team_data: TeamUpdate) -> Optional[TeamResponse]:
        """Update team."""
        # Validate team exists
        validation_result = self.validator.validate_team_exists(team_id)
        if not validation_result.is_valid:
            raise ValueError(f"Team validation failed: {validation_result.errors}")
        
        team = await self.repository.find_by_id(team_id)
        if not team:
            return None
        
        # Validate update data
        validation_result = self.validator.validate_team_update(team_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid update data: {validation_result.errors}")
        
        # Check for duplicate name if name is being updated
        if team_data.name and team_data.name != team.name:
            if await self.repository.exists_by_name(team_data.name, exclude_id=team_id):
                raise ValueError(f"Team with name '{team_data.name}' already exists")
        
        # Update fields
        if team_data.name is not None:
            team.name = team_data.name
        if team_data.address is not None:
            team.address = team_data.address
        if team_data.phone is not None:
            team.phone = team_data.phone
        if team_data.email is not None:
            team.email = team_data.email
        
        saved_team = await self.repository.save(team)
        return TeamResponse.model_validate(saved_team)
    
    async def delete_team(self, team_id: int) -> bool:
        """Delete team."""
        # Check if team has robots (business rule)
        team = await self.repository.find_by_id(team_id)
        if not team:
            return False
        
        # This would need to be implemented with robot repository
        # For now, we'll allow deletion
        return await self.repository.delete(team_id)
    
    async def get_teams_by_tournament(self, tournament_id: int) -> List[TeamResponse]:
        """Get all teams for a tournament."""
        teams = await self.repository.find_by_tournament(tournament_id)
        return [TeamResponse.model_validate(team) for team in teams]
    
    # Robot Management Methods (simplified - would need RobotRepository)
    async def create_robot(self, team_id: int, robot_data: RobotCreate) -> RobotResponse:
        """Create a robot for a team."""
        # Validate team exists
        team = await self.repository.find_by_id(team_id)
        if not team:
            raise ValueError("Team not found")
        
        # This would need RobotRepository implementation
        # For now, return a placeholder
        raise NotImplementedError("Robot creation needs RobotRepository implementation")
    
    async def get_robots(self, team_id: int) -> List[RobotResponse]:
        """Get robots for a team."""
        # This would need RobotRepository implementation
        # For now, return empty list
        return []
    
    # Player Management Methods (simplified - would need PlayerRepository)
    async def create_player(self, team_id: int, player_data: PlayerCreate) -> PlayerResponse:
        """Create a player for a team."""
        # Validate team exists
        team = await self.repository.find_by_id(team_id)
        if not team:
            raise ValueError("Team not found")
        
        # This would need PlayerRepository implementation
        # For now, return a placeholder
        raise NotImplementedError("Player creation needs PlayerRepository implementation")
    
    async def get_players(self, team_id: int) -> List[PlayerResponse]:
        """Get players for a team."""
        # This would need PlayerRepository implementation
        # For now, return empty list
        return []
    
    # Robot Class Management Methods (simplified - would need RobotClassRepository)
    async def get_robot_classes(self) -> List[RobotClassResponse]:
        """Get all robot classes."""
        # This would need RobotClassRepository implementation
        # For now, return empty list
        return []
    
    async def get_robot_class(self, robot_class_id: int) -> Optional[RobotClassResponse]:
        """Get robot class by ID."""
        # This would need RobotClassRepository implementation
        # For now, return None
        return None
    
    async def create_robot_class(self, robot_class_data: RobotClassCreate) -> RobotClassResponse:
        """Create a new robot class."""
        # This would need RobotClassRepository implementation
        # For now, return a placeholder
        raise NotImplementedError("Robot class creation needs RobotClassRepository implementation")
    
    async def update_robot_class(self, robot_class_id: int, robot_class_data: RobotClassUpdate) -> Optional[RobotClassResponse]:
        """Update robot class."""
        # This would need RobotClassRepository implementation
        # For now, return None
        return None
    
    async def delete_robot_class(self, robot_class_id: int) -> bool:
        """Delete robot class."""
        # This would need RobotClassRepository implementation
        # For now, return False
        return False
