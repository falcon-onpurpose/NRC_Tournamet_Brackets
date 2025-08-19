"""
Tournament service for managing tournament operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from config import Settings
from models import Tournament, RobotClass, Team, SwissMatch, EliminationMatch
from schemas import TournamentCreate, TournamentUpdate, TournamentResponse
from .validation_service import ValidationService


class TournamentService:
    """
    Service for tournament management operations.
    Handles CRUD operations and business logic for tournaments.
    """
    
    def __init__(self, settings: Settings, session: Optional[AsyncSession] = None):
        self.settings = settings
        self.session = session
        self.validation_service = ValidationService()
    
    async def create_tournament(self, data: TournamentCreate, session: Optional[AsyncSession] = None) -> Tournament:
        """
        Create a new tournament.
        
        Args:
            data: Tournament creation data
            session: Database session (optional)
            
        Returns:
            Created tournament
            
        Raises:
            ValueError: If validation fails
        """
        # Validate tournament data
        validation_result = self.validation_service.validate_tournament_data(data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid tournament data: {validation_result.errors}")
        
        # Use provided session or create new one
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Create tournament
        tournament = Tournament(
            name=data.name,
            format=data.format,
            status="setup",
            location=data.location,
            description=data.description,
            swiss_rounds=data.swiss_rounds,
            start_date=data.start_date,
            end_date=data.end_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db_session.add(tournament)
        await db_session.commit()
        await db_session.refresh(tournament)
        
        return tournament
    
    async def get_tournament(self, tournament_id: int, session: Optional[AsyncSession] = None) -> Tournament:
        """
        Get tournament by ID.
        
        Args:
            tournament_id: Tournament ID
            session: Database session (optional)
            
        Returns:
            Tournament
            
        Raises:
            ValueError: If tournament not found
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Query tournament with related data
        stmt = select(Tournament).where(Tournament.id == tournament_id)
        result = await db_session.execute(stmt)
        tournament = result.scalar_one_or_none()
        
        if not tournament:
            raise ValueError(f"Tournament with ID {tournament_id} not found")
        
        return tournament
    
    async def get_tournaments(self, 
                            filters: Optional[Dict[str, Any]] = None,
                            session: Optional[AsyncSession] = None) -> List[Tournament]:
        """
        Get tournaments with optional filters.
        
        Args:
            filters: Optional filters
            session: Database session (optional)
            
        Returns:
            List of tournaments
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Build query
        stmt = select(Tournament)
        
        # Apply filters
        if filters:
            if "status" in filters:
                stmt = stmt.where(Tournament.status == filters["status"])
            if "format" in filters:
                stmt = stmt.where(Tournament.format == filters["format"])
            if "location" in filters:
                stmt = stmt.where(Tournament.location == filters["location"])
        
        # Order by creation date
        stmt = stmt.order_by(Tournament.created_at.desc())
        
        result = await db_session.execute(stmt)
        tournaments = result.scalars().all()
        
        return list(tournaments)
    
    async def update_tournament(self, 
                              tournament_id: int, 
                              data: TournamentUpdate,
                              session: Optional[AsyncSession] = None) -> Tournament:
        """
        Update tournament.
        
        Args:
            tournament_id: Tournament ID
            data: Update data
            session: Database session (optional)
            
        Returns:
            Updated tournament
            
        Raises:
            ValueError: If tournament not found or validation fails
        """
        # Validate update data
        validation_result = self.validation_service.validate_tournament_update(data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid tournament update data: {validation_result.errors}")
        
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Get existing tournament
        tournament = await self.get_tournament(tournament_id, db_session)
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(tournament, field, value)
        
        await db_session.commit()
        await db_session.refresh(tournament)
        
        return tournament
    
    async def delete_tournament(self, tournament_id: int, session: Optional[AsyncSession] = None) -> bool:
        """
        Delete tournament.
        
        Args:
            tournament_id: Tournament ID
            session: Database session (optional)
            
        Returns:
            True if deleted successfully
            
        Raises:
            ValueError: If tournament not found
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Check if tournament exists
        tournament = await self.get_tournament(tournament_id, db_session)
        
        # Check if tournament can be deleted (no active matches)
        if tournament.status in ["active", "running"]:
            raise ValueError(f"Cannot delete tournament {tournament_id} - tournament is active")
        
        # Delete tournament
        stmt = delete(Tournament).where(Tournament.id == tournament_id)
        await db_session.execute(stmt)
        await db_session.commit()
        
        return True
    
    async def start_tournament(self, tournament_id: int, session: Optional[AsyncSession] = None) -> Tournament:
        """
        Start a tournament.
        
        Args:
            tournament_id: Tournament ID
            session: Database session (optional)
            
        Returns:
            Updated tournament
            
        Raises:
            ValueError: If tournament cannot be started
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Get tournament
        tournament = await self.get_tournament(tournament_id, db_session)
        
        # Validate tournament can be started
        if tournament.status != "setup":
            raise ValueError(f"Tournament {tournament_id} cannot be started - status is {tournament.status}")
        
        # Check if tournament has teams
        teams_stmt = select(Team).where(Team.tournament_id == tournament_id)
        teams_result = await db_session.execute(teams_stmt)
        teams = teams_result.scalars().all()
        
        if not teams:
            raise ValueError(f"Tournament {tournament_id} cannot be started - no teams registered")
        
        # Update tournament status
        tournament.status = "active"
        tournament.updated_at = datetime.utcnow()
        
        await db_session.commit()
        await db_session.refresh(tournament)
        
        return tournament
    
    async def pause_tournament(self, tournament_id: int, session: Optional[AsyncSession] = None) -> Tournament:
        """
        Pause a tournament.
        
        Args:
            tournament_id: Tournament ID
            session: Database session (optional)
            
        Returns:
            Updated tournament
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Get tournament
        tournament = await self.get_tournament(tournament_id, db_session)
        
        # Validate tournament can be paused
        if tournament.status not in ["active", "running"]:
            raise ValueError(f"Tournament {tournament_id} cannot be paused - status is {tournament.status}")
        
        # Update tournament status
        tournament.status = "paused"
        tournament.updated_at = datetime.utcnow()
        
        await db_session.commit()
        await db_session.refresh(tournament)
        
        return tournament
    
    async def resume_tournament(self, tournament_id: int, session: Optional[AsyncSession] = None) -> Tournament:
        """
        Resume a paused tournament.
        
        Args:
            tournament_id: Tournament ID
            session: Database session (optional)
            
        Returns:
            Updated tournament
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Get tournament
        tournament = await self.get_tournament(tournament_id, db_session)
        
        # Validate tournament can be resumed
        if tournament.status != "paused":
            raise ValueError(f"Tournament {tournament_id} cannot be resumed - status is {tournament.status}")
        
        # Update tournament status
        tournament.status = "active"
        tournament.updated_at = datetime.utcnow()
        
        await db_session.commit()
        await db_session.refresh(tournament)
        
        return tournament
    
    async def complete_tournament(self, tournament_id: int, session: Optional[AsyncSession] = None) -> Tournament:
        """
        Complete a tournament.
        
        Args:
            tournament_id: Tournament ID
            session: Database session (optional)
            
        Returns:
            Updated tournament
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Get tournament
        tournament = await self.get_tournament(tournament_id, db_session)
        
        # Validate tournament can be completed
        if tournament.status not in ["active", "running", "paused"]:
            raise ValueError(f"Tournament {tournament_id} cannot be completed - status is {tournament.status}")
        
        # Update tournament status
        tournament.status = "completed"
        tournament.updated_at = datetime.utcnow()
        tournament.end_date = datetime.utcnow()
        
        await db_session.commit()
        await db_session.refresh(tournament)
        
        return tournament
    
    async def get_tournament_stats(self, tournament_id: int, session: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        Get tournament statistics.
        
        Args:
            tournament_id: Tournament ID
            session: Database session (optional)
            
        Returns:
            Tournament statistics
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Get tournament
        tournament = await self.get_tournament(tournament_id, db_session)
        
        # Get team count
        teams_stmt = select(Team).where(Team.tournament_id == tournament_id)
        teams_result = await db_session.execute(teams_stmt)
        team_count = len(teams_result.scalars().all())
        
        # Get match counts
        swiss_matches_stmt = select(SwissMatch).where(SwissMatch.tournament_id == tournament_id)
        swiss_result = await db_session.execute(swiss_matches_stmt)
        swiss_match_count = len(swiss_result.scalars().all())
        
        elimination_matches_stmt = select(EliminationMatch).where(EliminationMatch.tournament_id == tournament_id)
        elimination_result = await db_session.execute(elimination_matches_stmt)
        elimination_match_count = len(elimination_result.scalars().all())
        
        # Get completed match count
        completed_swiss_stmt = select(SwissMatch).where(
            SwissMatch.tournament_id == tournament_id,
            SwissMatch.status == "completed"
        )
        completed_swiss_result = await db_session.execute(completed_swiss_stmt)
        completed_swiss_count = len(completed_swiss_result.scalars().all())
        
        completed_elimination_stmt = select(EliminationMatch).where(
            EliminationMatch.tournament_id == tournament_id,
            EliminationMatch.status == "completed"
        )
        completed_elimination_result = await db_session.execute(completed_elimination_stmt)
        completed_elimination_count = len(completed_elimination_result.scalars().all())
        
        return {
            "tournament_id": tournament_id,
            "tournament_name": tournament.name,
            "status": tournament.status,
            "team_count": team_count,
            "total_matches": swiss_match_count + elimination_match_count,
            "completed_matches": completed_swiss_count + completed_elimination_count,
            "swiss_matches": swiss_match_count,
            "elimination_matches": elimination_match_count,
            "progress_percentage": (
                (completed_swiss_count + completed_elimination_count) / 
                max(swiss_match_count + elimination_match_count, 1) * 100
            )
        }
