"""
Team Service - Handles team registration, robot management, and player handling.

This service provides business logic for:
- Team registration and management
- Robot registration and class assignment
- Player management and team associations
- CSV import processing for team registration
- Team validation and conflict resolution
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select

from models import Team, Robot, Player, RobotClass, Tournament
from schemas import (
    TeamCreate, TeamUpdate, TeamResponse,
    RobotCreate, RobotUpdate, RobotResponse,
    PlayerCreate, PlayerUpdate, PlayerResponse,
    RobotClassCreate, RobotClassUpdate, RobotClassResponse,
    TeamRegistrationResponse, TeamImportResponse
)
from services.validation_service import ValidationService
from services.csv_import_service import CSVImportService, ImportResult


class TeamService:
    """Service for managing teams, robots, and players."""
    
    def __init__(self, settings):
        self.settings = settings
        self.validation_service = ValidationService()
        self.csv_import_service = CSVImportService(settings)
    
    # Team Management Methods
    
    async def create_team(
        self,
        session: AsyncSession,
        team_data: TeamCreate
    ) -> TeamResponse:
        """Create a new team."""
        # Validate team data
        validation_result = self.validation_service.validate_team_data(team_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid team data: {validation_result.errors}")
        
        # Check for duplicate team names
        result = await session.execute(
            select(Team).where(Team.name == team_data.name)
        )
        existing_team = result.scalar_one_or_none()
        
        if existing_team:
            raise ValueError(f"Team with name '{team_data.name}' already exists")
        
        # Create team
        team = Team(**team_data.model_dump())
        session.add(team)
        await session.commit()
        await session.refresh(team)
        
        return TeamResponse.model_validate(team)
    
    async def get_team(
        self,
        session: AsyncSession,
        team_id: int
    ) -> Optional[TeamResponse]:
        """Get a team by ID."""
        result = await session.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()
        if not team:
            return None
        
        return TeamResponse.model_validate(team)
    
    async def get_teams(
        self,
        session: AsyncSession,
        tournament_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TeamResponse]:
        """Get teams with optional filtering."""
        stmt = select(Team)
        
        if tournament_id:
            stmt = stmt.where(Team.tournament_id == tournament_id)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
        teams = result.scalars().all()
        return [TeamResponse.model_validate(team) for team in teams]
    
    async def update_team(
        self,
        session: AsyncSession,
        team_id: int,
        team_data: TeamUpdate
    ) -> Optional[TeamResponse]:
        """Update a team."""
        result = await session.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()
        if not team:
            return None
        
        # Validate update data
        validation_result = self.validation_service.validate_team_update(team_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid team update data: {validation_result.errors}")
        
        # Check for name conflicts if name is being updated
        if team_data.name and team_data.name != team.name:
            result = await session.execute(
                select(Team).where(
                    and_(
                        Team.name == team_data.name,
                        Team.id != team_id
                    )
                )
            )
            existing_team = result.scalar_one_or_none()
            
            if existing_team:
                raise ValueError(f"Team with name '{team_data.name}' already exists")
        
        # Update team
        update_data = team_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(team, field, value)
        
        await session.commit()
        await session.refresh(team)
        
        return TeamResponse.model_validate(team)
    
    async def delete_team(
        self,
        session: AsyncSession,
        team_id: int
    ) -> bool:
        """Delete a team."""
        result = await session.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()
        if not team:
            return False
        
        # Check if team has active robots or players
        robot_count_result = await session.execute(
            select(Robot).where(Robot.team_id == team_id)
        )
        active_robots = len(robot_count_result.scalars().all())
        
        player_count_result = await session.execute(
            select(Player).where(Player.team_id == team_id)
        )
        active_players = len(player_count_result.scalars().all())
        
        if active_robots > 0 or active_players > 0:
            raise ValueError("Cannot delete team with active robots or players")
        
        await session.delete(team)
        await session.commit()
        return True
    
    # Robot Management Methods
    
    async def create_robot(
        self,
        session: AsyncSession,
        robot_data: RobotCreate
    ) -> RobotResponse:
        """Create a new robot."""
        # Validate robot data
        validation_result = self.validation_service.validate_robot_data(robot_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid robot data: {validation_result.errors}")
        
        # Verify team exists
        team_result = await session.execute(
            select(Team).where(Team.id == robot_data.team_id)
        )
        team = team_result.scalar_one_or_none()
        if not team:
            raise ValueError(f"Team with ID {robot_data.team_id} does not exist")
        
        # Verify robot class exists
        robot_class_result = await session.execute(
            select(RobotClass).where(RobotClass.id == robot_data.robot_class_id)
        )
        robot_class = robot_class_result.scalar_one_or_none()
        if not robot_class:
            raise ValueError(f"Robot class with ID {robot_data.robot_class_id} does not exist")
        
        # Check for duplicate robot names within the team
        existing_robot_result = await session.execute(
            select(Robot).where(
                and_(
                    Robot.name == robot_data.name,
                    Robot.team_id == robot_data.team_id
                )
            )
        )
        existing_robot = existing_robot_result.scalar_one_or_none()
        
        if existing_robot:
            raise ValueError(f"Robot with name '{robot_data.name}' already exists in team")
        
        # Create robot
        robot = Robot(**robot_data.model_dump())
        session.add(robot)
        await session.commit()
        await session.refresh(robot)
        
        return RobotResponse.model_validate(robot)
    
    async def get_robot(
        self,
        session: AsyncSession,
        robot_id: int
    ) -> Optional[RobotResponse]:
        """Get a robot by ID."""
        result = await session.execute(
            select(Robot).where(Robot.id == robot_id)
        )
        robot = result.scalar_one_or_none()
        if not robot:
            return None
        
        return RobotResponse.model_validate(robot)
    
    async def get_team_robots(
        self,
        session: AsyncSession,
        team_id: int
    ) -> List[RobotResponse]:
        """Get all robots for a team."""
        result = await session.execute(
            select(Robot).where(Robot.team_id == team_id)
        )
        robots = result.scalars().all()
        return [RobotResponse.model_validate(robot) for robot in robots]
    
    async def update_robot(
        self,
        session: AsyncSession,
        robot_id: int,
        robot_data: RobotUpdate
    ) -> Optional[RobotResponse]:
        """Update a robot."""
        result = await session.execute(
            select(Robot).where(Robot.id == robot_id)
        )
        robot = result.scalar_one_or_none()
        if not robot:
            return None
        
        # Validate update data
        validation_result = self.validation_service.validate_robot_update(robot_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid robot update data: {validation_result.errors}")
        
        # Check for name conflicts if name is being updated
        if robot_data.name and robot_data.name != robot.name:
            existing_result = await session.execute(
                select(Robot).where(
                    and_(
                        Robot.name == robot_data.name,
                        Robot.team_id == robot.team_id,
                        Robot.id != robot_id
                    )
                )
            )
            existing_robot = existing_result.scalar_one_or_none()
            
            if existing_robot:
                raise ValueError(f"Robot with name '{robot_data.name}' already exists in team")
        
        # Update robot
        update_data = robot_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(robot, field, value)
        
        await session.commit()
        await session.refresh(robot)
        
        return RobotResponse.model_validate(robot)
    
    async def delete_robot(
        self,
        session: AsyncSession,
        robot_id: int
    ) -> bool:
        """Delete a robot."""
        result = await session.execute(
            select(Robot).where(Robot.id == robot_id)
        )
        robot = result.scalar_one_or_none()
        if not robot:
            return False
        
        # Check if robot is in active matches
        # This would need to be implemented based on match status
        # For now, we'll allow deletion
        
        await session.delete(robot)
        await session.commit()
        return True
    
    # Player Management Methods
    
    async def create_player(
        self,
        session: AsyncSession,
        player_data: PlayerCreate
    ) -> PlayerResponse:
        """Create a new player."""
        # Validate player data
        validation_result = self.validation_service.validate_player_data(player_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid player data: {validation_result.errors}")
        
        # Verify team exists
        team_result = await session.execute(
            select(Team).where(Team.id == player_data.team_id)
        )
        team = team_result.scalar_one_or_none()
        if not team:
            raise ValueError(f"Team with ID {player_data.team_id} does not exist")
        
        # Check for duplicate player names within the team
        existing_result = await session.execute(
            select(Player).where(
                and_(
                    Player.name == player_data.name,
                    Player.team_id == player_data.team_id
                )
            )
        )
        existing_player = existing_result.scalar_one_or_none()
        
        if existing_player:
            raise ValueError(f"Player with name '{player_data.name}' already exists in team")
        
        # Create player
        player = Player(**player_data.model_dump())
        session.add(player)
        await session.commit()
        await session.refresh(player)
        
        return PlayerResponse.model_validate(player)
    
    async def get_player(
        self,
        session: AsyncSession,
        player_id: int
    ) -> Optional[PlayerResponse]:
        """Get a player by ID."""
        result = await session.execute(
            select(Player).where(Player.id == player_id)
        )
        player = result.scalar_one_or_none()
        if not player:
            return None
        
        return PlayerResponse.model_validate(player)
    
    async def get_team_players(
        self,
        session: AsyncSession,
        team_id: int
    ) -> List[PlayerResponse]:
        """Get all players for a team."""
        result = await session.execute(
            select(Player).where(Player.team_id == team_id)
        )
        players = result.scalars().all()
        return [PlayerResponse.model_validate(player) for player in players]
    
    async def update_player(
        self,
        session: AsyncSession,
        player_id: int,
        player_data: PlayerUpdate
    ) -> Optional[PlayerResponse]:
        """Update a player."""
        result = await session.execute(
            select(Player).where(Player.id == player_id)
        )
        player = result.scalar_one_or_none()
        if not player:
            return None
        
        # Validate update data
        validation_result = self.validation_service.validate_player_update(player_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid player update data: {validation_result.errors}")
        
        # Check for name conflicts if name is being updated
        if player_data.name and player_data.name != player.name:
            existing_result = await session.execute(
                select(Player).where(
                    and_(
                        Player.name == player_data.name,
                        Player.team_id == player.team_id,
                        Player.id != player_id
                    )
                )
            )
            existing_player = existing_result.scalar_one_or_none()
            
            if existing_player:
                raise ValueError(f"Player with name '{player_data.name}' already exists in team")
        
        # Update player
        update_data = player_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(player, field, value)
        
        await session.commit()
        await session.refresh(player)
        
        return PlayerResponse.model_validate(player)
    
    async def delete_player(
        self,
        session: AsyncSession,
        player_id: int
    ) -> bool:
        """Delete a player."""
        result = await session.execute(
            select(Player).where(Player.id == player_id)
        )
        player = result.scalar_one_or_none()
        if not player:
            return False
        
        await session.delete(player)
        await session.commit()
        return True
    
    # CSV Import Methods
    
    async def import_teams_from_csv(
        self,
        session: AsyncSession,
        csv_data: List[Dict[str, Any]],
        tournament_id: int,
        strict_mode: bool = False
    ) -> TeamImportResponse:
        """
        Import teams from CSV data with comprehensive validation.
        
        Args:
            session: Database session
            csv_data: List of CSV row dictionaries
            tournament_id: Tournament ID to associate data with
            strict_mode: If True, fail on any validation error
            
        Returns:
            TeamImportResponse with detailed results
        """
        # Verify tournament exists
        result = await session.execute(
            select(Tournament).where(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError(f"Tournament with ID {tournament_id} does not exist")
        
        # Use enhanced CSV import service for validation and processing
        import_result = self.csv_import_service.import_tournament_data(
            csv_data, tournament_id, strict_mode
        )
        
        imported_teams = []
        all_errors = []
        
        # Convert import errors to the expected format
        for error in import_result.errors + import_result.warnings:
            all_errors.append({
                "row": error.row,
                "column": error.column,
                "severity": error.severity.value,
                "error": error.message,
                "original_value": error.original_value,
                "corrected_value": error.corrected_value
            })
        
        # Create teams from validated data
        for team_data in import_result.teams_created:
            try:
                team_create = TeamCreate(**team_data)
                team = await self.create_team(session, team_create)
                imported_teams.append(team)
            except Exception as e:
                all_errors.append({
                    "row": 0,
                    "column": "team_creation",
                    "severity": "error",
                    "error": f"Failed to create team: {str(e)}",
                    "original_value": team_data,
                    "corrected_value": None
                })
        
        return TeamImportResponse(
            imported_count=len(imported_teams),
            error_count=len([e for e in all_errors if e["severity"] in ["error", "critical"]]),
            teams=imported_teams,
            errors=all_errors,
            import_report=self.csv_import_service.generate_import_report(import_result),
            validation_summary={
                "total_rows": import_result.total_rows,
                "processed_rows": import_result.processed_rows,
                "teams_found": len(import_result.teams_created),
                "robots_found": len(import_result.robots_created),
                "players_found": len(import_result.players_created),
                "warnings": len(import_result.warnings),
                "errors": len(import_result.errors)
            }
        )
    
    def _parse_csv_row(
        self,
        row: Dict[str, Any],
        tournament_id: int
    ) -> TeamCreate:
        """Parse a CSV row into TeamCreate data."""
        # Map CSV columns to team fields
        # This mapping should be configurable based on the CSV format
        team_data = {
            "name": row.get("Team", "").strip(),
            "email": row.get("Email", "").strip(),
            "phone": row.get("Team_Phone", "").strip(),
            "address": row.get("Team_Address", "").strip()
        }
        
        # Validate required fields
        if not team_data["name"]:
            raise ValueError("Team name is required")
        
        return TeamCreate(**team_data)
    
    # Utility Methods
    
    async def get_team_statistics(
        self,
        session: AsyncSession,
        team_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive statistics for a team."""
        result = await session.execute(
            select(Team).where(Team.id == team_id)
        )
        team = result.scalar_one_or_none()
        if not team:
            return {}
        
        # Count robots and players
        robot_result = await session.execute(
            select(Robot).where(Robot.team_id == team_id)
        )
        robot_count = len(robot_result.scalars().all())
        
        player_result = await session.execute(
            select(Player).where(Player.team_id == team_id)
        )
        player_count = len(player_result.scalars().all())
        
        # Get robot class distribution
        robot_classes_result = await session.execute(
            select(Robot.robot_class_id).where(Robot.team_id == team_id)
        )
        robot_classes = robot_classes_result.scalars().all()
        
        class_distribution = {}
        for robot_class_id in robot_classes:
            class_name_result = await session.execute(
                select(RobotClass.name).where(RobotClass.id == robot_class_id)
            )
            class_name = class_name_result.scalar()
            if class_name:
                class_distribution[class_name] = class_distribution.get(class_name, 0) + 1
        
        return {
            "team_id": team_id,
            "team_name": team.name,
            "robot_count": robot_count,
            "player_count": player_count,
            "robot_class_distribution": class_distribution,
            "created_at": team.created_at,
            "updated_at": team.updated_at
        }
    
    async def search_teams(
        self,
        session: AsyncSession,
        search_term: str,
        tournament_id: Optional[int] = None
    ) -> List[TeamResponse]:
        """Search teams by name or other criteria."""
        stmt = select(Team).where(
            or_(
                Team.name.ilike(f"%{search_term}%"),
                Team.contact_email.ilike(f"%{search_term}%"),
                Team.notes.ilike(f"%{search_term}%")
            )
        )
        
        if tournament_id:
            stmt = stmt.where(Team.tournament_id == tournament_id)
        
        result = await session.execute(stmt)
        teams = result.scalars().all()
        return [TeamResponse.model_validate(team) for team in teams]

    # Robot Class Management Methods
    
    async def get_robot_classes(
        self,
        session: AsyncSession
    ) -> List[RobotClassResponse]:
        """Get all robot classes."""
        result = await session.execute(select(RobotClass))
        robot_classes = result.scalars().all()
        return [RobotClassResponse.model_validate(rc) for rc in robot_classes]
    
    async def get_robot_class(
        self,
        session: AsyncSession,
        robot_class_id: int
    ) -> Optional[RobotClassResponse]:
        """Get robot class by ID."""
        result = await session.execute(
            select(RobotClass).where(RobotClass.id == robot_class_id)
        )
        robot_class = result.scalar_one_or_none()
        if not robot_class:
            return None
        
        return RobotClassResponse.model_validate(robot_class)
    
    async def create_robot_class(
        self,
        session: AsyncSession,
        robot_class_data: RobotClassCreate
    ) -> RobotClassResponse:
        """Create a new robot class."""
        # Check for duplicate names
        result = await session.execute(
            select(RobotClass).where(RobotClass.name == robot_class_data.name)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"Robot class with name '{robot_class_data.name}' already exists")
        
        # Create robot class
        robot_class = RobotClass(**robot_class_data.model_dump())
        session.add(robot_class)
        await session.commit()
        await session.refresh(robot_class)
        
        return RobotClassResponse.model_validate(robot_class)
    
    async def update_robot_class(
        self,
        session: AsyncSession,
        robot_class_id: int,
        robot_class_data: RobotClassUpdate
    ) -> Optional[RobotClassResponse]:
        """Update robot class."""
        result = await session.execute(
            select(RobotClass).where(RobotClass.id == robot_class_id)
        )
        robot_class = result.scalar_one_or_none()
        if not robot_class:
            return None
        
        # Check for name conflicts if name is being updated
        if robot_class_data.name and robot_class_data.name != robot_class.name:
            existing_result = await session.execute(
                select(RobotClass).where(
                    and_(
                        RobotClass.name == robot_class_data.name,
                        RobotClass.id != robot_class_id
                    )
                )
            )
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                raise ValueError(f"Robot class with name '{robot_class_data.name}' already exists")
        
        # Update robot class
        update_data = robot_class_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(robot_class, field, value)
        
        await session.commit()
        await session.refresh(robot_class)
        
        return RobotClassResponse.model_validate(robot_class)
    
    async def delete_robot_class(
        self,
        session: AsyncSession,
        robot_class_id: int
    ) -> bool:
        """Delete robot class."""
        result = await session.execute(
            select(RobotClass).where(RobotClass.id == robot_class_id)
        )
        robot_class = result.scalar_one_or_none()
        if not robot_class:
            return False
        
        # Check if robot class is in use
        robots_result = await session.execute(
            select(Robot).where(Robot.robot_class_id == robot_class_id)
        )
        robots_using_class = robots_result.scalars().all()
        
        if robots_using_class:
            raise ValueError("Cannot delete robot class with active robots")
        
        await session.delete(robot_class)
        await session.commit()
        return True
