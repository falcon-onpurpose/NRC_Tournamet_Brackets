"""
Tournament service for business logic operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from domain.tournament.tournament_repository import TournamentRepository
from domain.tournament.tournament_validator import TournamentValidator
from schemas import TournamentCreate, TournamentUpdate, TournamentResponse


class TournamentService:
    """Service for tournament business logic operations."""
    
    def __init__(self):
        self.repository = TournamentRepository()
        self.validator = TournamentValidator()
    
    async def get_tournaments(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[TournamentResponse]:
        """Get tournaments with optional filtering."""
        tournaments = await self.repository.get_tournaments(
            session=session,
            skip=skip,
            limit=limit,
            status=status
        )
        
        return [TournamentResponse.from_orm(tournament) for tournament in tournaments]
    
    async def get_tournament(
        self,
        session: AsyncSession,
        tournament_id: int
    ) -> Optional[TournamentResponse]:
        """Get tournament by ID."""
        tournament = await self.repository.get_tournament_by_id(
            session=session,
            tournament_id=tournament_id
        )
        
        if not tournament:
            return None
        
        return TournamentResponse.from_orm(tournament)
    
    async def create_tournament(
        self,
        session: AsyncSession,
        tournament_data: TournamentCreate
    ) -> TournamentResponse:
        """Create a new tournament."""
        # Validate tournament data
        validation_result = await self.validator.validate_tournament_create(tournament_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid tournament data: {validation_result.errors}")
        
        # Convert to dict for repository
        data_dict = tournament_data.dict()
        
        # Create tournament
        tournament = await self.repository.create_tournament(
            session=session,
            tournament_data=data_dict
        )
        
        return TournamentResponse.from_orm(tournament)
    
    async def update_tournament(
        self,
        session: AsyncSession,
        tournament_id: int,
        tournament_data: TournamentUpdate
    ) -> Optional[TournamentResponse]:
        """Update tournament."""
        # Validate tournament data
        validation_result = await self.validator.validate_tournament_update(tournament_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid tournament data: {validation_result.errors}")
        
        # Convert to dict for repository
        data_dict = tournament_data.dict(exclude_unset=True)
        
        # Update tournament
        tournament = await self.repository.update_tournament(
            session=session,
            tournament_id=tournament_id,
            tournament_data=data_dict
        )
        
        if not tournament:
            return None
        
        return TournamentResponse.from_orm(tournament)
    
    async def delete_tournament(
        self,
        session: AsyncSession,
        tournament_id: int
    ) -> bool:
        """Delete tournament."""
        return await self.repository.delete_tournament(
            session=session,
            tournament_id=tournament_id
        )
    
    async def get_tournament_teams(
        self,
        session: AsyncSession,
        tournament_id: int
    ) -> List[Dict[str, Any]]:
        """Get all teams for a tournament."""
        teams = await self.repository.get_tournament_teams(
            session=session,
            tournament_id=tournament_id
        )
        
        return [
            {
                "id": str(team.id),
                "name": team.name,
                "experience_level": team.experience_level,
                "created_at": team.created_at.isoformat() if team.created_at else None
            }
            for team in teams
        ]
    
    async def get_tournament_matches(
        self,
        session: AsyncSession,
        tournament_id: int
    ) -> List[Dict[str, Any]]:
        """Get all matches for a tournament."""
        return await self.repository.get_tournament_matches(
            session=session,
            tournament_id=tournament_id
        )
    
    async def start_tournament(
        self,
        session: AsyncSession,
        tournament_id: int
    ) -> bool:
        """Start a tournament."""
        tournament = await self.repository.get_tournament_by_id(
            session=session,
            tournament_id=tournament_id
        )
        
        if not tournament:
            return False
        
        if tournament.status != "upcoming":
            return False
        
        # Update tournament status to active
        await self.repository.update_tournament(
            session=session,
            tournament_id=tournament_id,
            tournament_data={"status": "active"}
        )
        
        return True
    
    async def end_tournament(
        self,
        session: AsyncSession,
        tournament_id: int
    ) -> bool:
        """End a tournament."""
        tournament = await self.repository.get_tournament_by_id(
            session=session,
            tournament_id=tournament_id
        )
        
        if not tournament:
            return False
        
        if tournament.status not in ["active", "upcoming"]:
            return False
        
        # Update tournament status to completed
        await self.repository.update_tournament(
            session=session,
            tournament_id=tournament_id,
            tournament_data={"status": "completed"}
        )
        
        return True
