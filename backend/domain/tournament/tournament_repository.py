"""
Tournament repository for data access operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from models import Tournament, Team, SwissMatch, EliminationMatch


class TournamentRepository:
    """Repository for tournament data access operations."""
    
    def __init__(self):
        pass
    
    async def get_tournaments(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Tournament]:
        """Get tournaments with optional filtering."""
        query = select(Tournament)
        
        if status:
            query = query.where(Tournament.status == status)
        
        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
    
    async def get_tournament_by_id(
        self,
        session: AsyncSession,
        tournament_id: int
    ) -> Optional[Tournament]:
        """Get tournament by ID."""
        stmt = select(Tournament).where(Tournament.id == tournament_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_tournament(
        self,
        session: AsyncSession,
        tournament_data: Dict[str, Any]
    ) -> Tournament:
        """Create a new tournament."""
        # Parse dates if they are strings
        start_date = tournament_data["start_date"]
        end_date = tournament_data["end_date"]
        
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        tournament = Tournament(
            name=tournament_data["name"],
            description=tournament_data["description"],
            start_date=start_date,
            end_date=end_date,
            swiss_rounds_count=tournament_data["swiss_rounds_count"],
            max_teams=tournament_data["max_teams"],
            status=tournament_data["status"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(tournament)
        await session.commit()
        await session.refresh(tournament)
        return tournament
    
    async def update_tournament(
        self,
        session: AsyncSession,
        tournament_id: int,
        tournament_data: Dict[str, Any]
    ) -> Optional[Tournament]:
        """Update tournament."""
        stmt = (
            update(Tournament)
            .where(Tournament.id == tournament_id)
            .values(
                **tournament_data,
                updated_at=datetime.utcnow()
            )
        )
        
        await session.execute(stmt)
        await session.commit()
        
        return await self.get_tournament_by_id(session, tournament_id)
    
    async def delete_tournament(
        self,
        session: AsyncSession,
        tournament_id: int
    ) -> bool:
        """Delete tournament."""
        stmt = delete(Tournament).where(Tournament.id == tournament_id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
    
    async def get_tournament_teams(
        self,
        session: AsyncSession,
        tournament_id: int
    ) -> List[Team]:
        """Get all teams for a tournament."""
        stmt = select(Team).where(Team.tournament_id == tournament_id)
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def get_tournament_matches(
        self,
        session: AsyncSession,
        tournament_id: int
    ) -> List[Dict[str, Any]]:
        """Get all matches for a tournament."""
        # Get Swiss matches
        swiss_stmt = select(SwissMatch).where(SwissMatch.tournament_id == tournament_id)
        swiss_result = await session.execute(swiss_stmt)
        swiss_matches = swiss_result.scalars().all()
        
        # Get elimination matches
        elim_stmt = select(EliminationMatch).where(EliminationMatch.tournament_id == tournament_id)
        elim_result = await session.execute(elim_stmt)
        elim_matches = elim_result.scalars().all()
        
        # Combine and format
        matches = []
        for match in swiss_matches:
            matches.append({
                "id": str(match.id),
                "type": "swiss",
                "team1_id": str(match.team1_id),
                "team2_id": str(match.team2_id),
                "status": match.status,
                "scheduled_time": match.scheduled_time,
                "arena": match.arena
            })
        
        for match in elim_matches:
            matches.append({
                "id": str(match.id),
                "type": "elimination",
                "team1_id": str(match.team1_id),
                "team2_id": str(match.team2_id),
                "status": match.status,
                "scheduled_time": match.scheduled_time,
                "arena": match.arena
            })
        
        return matches
