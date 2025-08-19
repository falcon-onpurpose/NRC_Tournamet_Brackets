"""
Match repository for data access operations.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime

from domain.shared.repository import BaseRepository
from models import SwissMatch, EliminationMatch, Team, Tournament


class MatchRepository(BaseRepository):
    """Repository for Match entity data access."""
    
    async def find_swiss_match_by_id(self, match_id: int) -> Optional[SwissMatch]:
        """Find Swiss match by ID."""
        result = await self.session.execute(
            select(SwissMatch).where(SwissMatch.id == match_id)
        )
        return result.scalar_one_or_none()
    
    async def find_elimination_match_by_id(self, match_id: int) -> Optional[EliminationMatch]:
        """Find elimination match by ID."""
        result = await self.session.execute(
            select(EliminationMatch).where(EliminationMatch.id == match_id)
        )
        return result.scalar_one_or_none()
    
    async def find_all_swiss_matches(self, **filters) -> List[SwissMatch]:
        """Find all Swiss matches with optional filters."""
        stmt = select(SwissMatch)
        
        if 'tournament_id' in filters:
            stmt = stmt.where(SwissMatch.tournament_id == filters['tournament_id'])
        if 'round_number' in filters:
            stmt = stmt.where(SwissMatch.round_number == filters['round_number'])
        if 'status' in filters:
            stmt = stmt.where(SwissMatch.status == filters['status'])
        if 'team1_id' in filters:
            stmt = stmt.where(SwissMatch.team1_id == filters['team1_id'])
        if 'team2_id' in filters:
            stmt = stmt.where(SwissMatch.team2_id == filters['team2_id'])
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_all_elimination_matches(self, **filters) -> List[EliminationMatch]:
        """Find all elimination matches with optional filters."""
        stmt = select(EliminationMatch)
        
        if 'tournament_id' in filters:
            stmt = stmt.where(EliminationMatch.tournament_id == filters['tournament_id'])
        if 'bracket_id' in filters:
            stmt = stmt.where(EliminationMatch.bracket_id == filters['bracket_id'])
        if 'round_number' in filters:
            stmt = stmt.where(EliminationMatch.round_number == filters['round_number'])
        if 'status' in filters:
            stmt = stmt.where(EliminationMatch.status == filters['status'])
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_pending_matches(self, tournament_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find pending matches for a tournament."""
        # Swiss matches
        swiss_stmt = select(SwissMatch).where(SwissMatch.status == "pending")
        if tournament_id:
            swiss_stmt = swiss_stmt.where(SwissMatch.tournament_id == tournament_id)
        
        # Elimination matches
        elim_stmt = select(EliminationMatch).where(EliminationMatch.status == "pending")
        if tournament_id:
            elim_stmt = elim_stmt.where(EliminationMatch.tournament_id == tournament_id)
        
        swiss_result = await self.session.execute(swiss_stmt)
        elim_result = await self.session.execute(elim_stmt)
        
        swiss_matches = swiss_result.scalars().all()
        elim_matches = elim_result.scalars().all()
        
        pending_matches = []
        
        # Convert Swiss matches to dict format
        for match in swiss_matches:
            pending_matches.append({
                "id": match.id,
                "type": "swiss",
                "tournament_id": match.tournament_id,
                "round_number": match.round_number,
                "team1_id": match.team1_id,
                "team2_id": match.team2_id,
                "status": match.status,
                "created_at": match.created_at.isoformat() if match.created_at else None
            })
        
        # Convert elimination matches to dict format
        for match in elim_matches:
            pending_matches.append({
                "id": match.id,
                "type": "elimination",
                "tournament_id": match.tournament_id,
                "bracket_id": match.bracket_id,
                "round_number": match.round_number,
                "team1_id": match.team1_id,
                "team2_id": match.team2_id,
                "status": match.status,
                "created_at": match.created_at.isoformat() if match.created_at else None
            })
        
        return pending_matches
    
    async def save_swiss_match(self, match: SwissMatch) -> SwissMatch:
        """Save Swiss match (create or update)."""
        self.session.add(match)
        await self.session.commit()
        await self.session.refresh(match)
        return match
    
    async def save_elimination_match(self, match: EliminationMatch) -> EliminationMatch:
        """Save elimination match (create or update)."""
        self.session.add(match)
        await self.session.commit()
        await self.session.refresh(match)
        return match
    
    async def delete_swiss_match(self, match_id: int) -> bool:
        """Delete Swiss match by ID."""
        match = await self.find_swiss_match_by_id(match_id)
        if match:
            await self.session.delete(match)
            await self.session.commit()
            return True
        return False
    
    async def delete_elimination_match(self, match_id: int) -> bool:
        """Delete elimination match by ID."""
        match = await self.find_elimination_match_by_id(match_id)
        if match:
            await self.session.delete(match)
            await self.session.commit()
            return True
        return False
    
    async def exists_swiss_match(self, match_id: int) -> bool:
        """Check if Swiss match exists."""
        result = await self.session.execute(
            select(SwissMatch.id).where(SwissMatch.id == match_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def exists_elimination_match(self, match_id: int) -> bool:
        """Check if elimination match exists."""
        result = await self.session.execute(
            select(EliminationMatch.id).where(EliminationMatch.id == match_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def get_match_statistics(self, tournament_id: Optional[int] = None) -> Dict[str, Any]:
        """Get match statistics."""
        # Swiss match statistics
        swiss_stmt = select(
            func.count(SwissMatch.id).label("total_swiss_matches"),
            func.count(SwissMatch.id).filter(SwissMatch.status == "completed").label("completed_swiss_matches"),
            func.count(SwissMatch.id).filter(SwissMatch.status == "pending").label("pending_swiss_matches")
        )
        
        if tournament_id:
            swiss_stmt = swiss_stmt.where(SwissMatch.tournament_id == tournament_id)
        
        # Elimination match statistics
        elim_stmt = select(
            func.count(EliminationMatch.id).label("total_elimination_matches"),
            func.count(EliminationMatch.id).filter(EliminationMatch.status == "completed").label("completed_elimination_matches"),
            func.count(EliminationMatch.id).filter(EliminationMatch.status == "pending").label("pending_elimination_matches")
        )
        
        if tournament_id:
            elim_stmt = elim_stmt.where(EliminationMatch.tournament_id == tournament_id)
        
        swiss_result = await self.session.execute(swiss_stmt)
        elim_result = await self.session.execute(elim_stmt)
        
        swiss_stats = swiss_result.first()
        elim_stats = elim_result.first()
        
        return {
            "swiss_matches": {
                "total": swiss_stats.total_swiss_matches or 0,
                "completed": swiss_stats.completed_swiss_matches or 0,
                "pending": swiss_stats.pending_swiss_matches or 0
            },
            "elimination_matches": {
                "total": elim_stats.total_elimination_matches or 0,
                "completed": elim_stats.completed_elimination_matches or 0,
                "pending": elim_stats.pending_elimination_matches or 0
            }
        }
    
    # Implement abstract methods from BaseRepository
    async def find_by_id(self, entity_id: int):
        """Find match by ID (returns SwissMatch or EliminationMatch)."""
        # Try Swiss match first
        swiss_match = await self.find_swiss_match_by_id(entity_id)
        if swiss_match:
            return swiss_match
        
        # Try elimination match
        elim_match = await self.find_elimination_match_by_id(entity_id)
        return elim_match
    
    async def find_all(self, **filters) -> List:
        """Find all matches with optional filters."""
        swiss_matches = await self.find_all_swiss_matches(**filters)
        elim_matches = await self.find_all_elimination_matches(**filters)
        return swiss_matches + elim_matches
    
    async def save(self, entity):
        """Save match (create or update)."""
        if isinstance(entity, SwissMatch):
            return await self.save_swiss_match(entity)
        elif isinstance(entity, EliminationMatch):
            return await self.save_elimination_match(entity)
        else:
            raise ValueError("Entity must be SwissMatch or EliminationMatch")
    
    async def delete(self, entity_id: int) -> bool:
        """Delete match by ID."""
        # Try Swiss match first
        if await self.delete_swiss_match(entity_id):
            return True
        
        # Try elimination match
        return await self.delete_elimination_match(entity_id)
    
    async def exists(self, entity_id: int) -> bool:
        """Check if match exists."""
        return await self.exists_swiss_match(entity_id) or await self.exists_elimination_match(entity_id)
