"""
Player repository for data access operations.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from models import Player
from domain.shared.repository import BaseRepository


class PlayerRepository(BaseRepository[Player]):
    """Repository for player data access operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def find_by_id(self, player_id: int) -> Optional[Player]:
        """Find player by ID with relationships loaded."""
        query = (
            select(Player)
            .options(selectinload(Player.team))
            .where(Player.id == player_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def find_all(self, **filters) -> List[Player]:
        """Find all players with optional filters."""
        query = (
            select(Player)
            .options(selectinload(Player.team))
        )
        
        # Apply filters
        if "team_id" in filters:
            query = query.where(Player.team_id == filters["team_id"])
        if "first_name" in filters:
            query = query.where(Player.first_name.ilike(f"%{filters['first_name']}%"))
        if "last_name" in filters:
            query = query.where(Player.last_name.ilike(f"%{filters['last_name']}%"))
        if "email" in filters:
            query = query.where(Player.email.ilike(f"%{filters['email']}%"))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def find_by_team(self, team_id: int) -> List[Player]:
        """Find all players for a specific team."""
        query = (
            select(Player)
            .options(selectinload(Player.team))
            .where(Player.team_id == team_id)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def find_by_name(self, first_name: str, last_name: str, team_id: Optional[int] = None) -> Optional[Player]:
        """Find player by full name, optionally within a specific team."""
        query = select(Player).where(
            and_(Player.first_name == first_name, Player.last_name == last_name)
        )
        
        if team_id:
            query = query.where(Player.team_id == team_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def find_by_email(self, email: str) -> List[Player]:
        """Find players by email address."""
        query = (
            select(Player)
            .options(selectinload(Player.team))
            .where(Player.email == email)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def search_by_name(self, search_term: str) -> List[Player]:
        """Search players by name (first or last name)."""
        query = (
            select(Player)
            .options(selectinload(Player.team))
            .where(
                Player.first_name.ilike(f"%{search_term}%") |
                Player.last_name.ilike(f"%{search_term}%")
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def save(self, player: Player) -> Player:
        """Save player (create or update)."""
        if player.id is None:
            # Creating new player
            self.session.add(player)
        else:
            # Updating existing player
            await self.session.merge(player)
        
        await self.session.commit()
        await self.session.refresh(player)
        return player
    
    async def delete(self, player_id: int) -> bool:
        """Delete player by ID."""
        player = await self.find_by_id(player_id)
        if player:
            await self.session.delete(player)
            await self.session.commit()
            return True
        return False
    
    async def exists(self, player_id: int) -> bool:
        """Check if player exists."""
        query = select(Player.id).where(Player.id == player_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_name(self, first_name: str, last_name: str, team_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if player name exists within a team."""
        query = select(Player.id).where(
            and_(
                Player.first_name == first_name,
                Player.last_name == last_name,
                Player.team_id == team_id
            )
        )
        
        if exclude_id:
            query = query.where(Player.id != exclude_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_email(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email exists."""
        if not email:
            return False
        
        query = select(Player.id).where(Player.email == email)
        
        if exclude_id:
            query = query.where(Player.id != exclude_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def count_by_team(self, team_id: int) -> int:
        """Count players in a specific team."""
        from sqlalchemy import func
        query = select(func.count(Player.id)).where(Player.team_id == team_id)
        result = await self.session.execute(query)
        return result.scalar() or 0
