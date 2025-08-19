"""
Team repository for data access operations.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from domain.shared.repository import BaseRepository
from models import Team, Robot, Player, RobotClass


class TeamRepository(BaseRepository[Team]):
    """Repository for Team entity data access."""
    
    async def find_by_id(self, team_id: int) -> Optional[Team]:
        """Find team by ID."""
        result = await self.session.execute(
            select(Team).where(Team.id == team_id)
        )
        return result.scalar_one_or_none()
    
    async def find_all(self, **filters) -> List[Team]:
        """Find all teams with optional filters."""
        stmt = select(Team)
        
        if 'tournament_id' in filters:
            stmt = stmt.where(Team.tournament_id == filters['tournament_id'])
        if 'name' in filters:
            stmt = stmt.where(Team.name.ilike(f"%{filters['name']}%"))
        if 'email' in filters:
            stmt = stmt.where(Team.email.ilike(f"%{filters['email']}%"))
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_name(self, name: str) -> Optional[Team]:
        """Find team by name."""
        result = await self.session.execute(
            select(Team).where(Team.name == name)
        )
        return result.scalar_one_or_none()
    
    async def find_by_tournament(self, tournament_id: int) -> List[Team]:
        """Find all teams for a tournament."""
        result = await self.session.execute(
            select(Team).where(Team.tournament_id == tournament_id)
        )
        return result.scalars().all()
    
    async def save(self, team: Team) -> Team:
        """Save team (create or update)."""
        self.session.add(team)
        await self.session.commit()
        await self.session.refresh(team)
        return team
    
    async def delete(self, team_id: int) -> bool:
        """Delete team by ID."""
        team = await self.find_by_id(team_id)
        if team:
            await self.session.delete(team)
            await self.session.commit()
            return True
        return False
    
    async def exists(self, team_id: int) -> bool:
        """Check if team exists."""
        result = await self.session.execute(
            select(Team.id).where(Team.id == team_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def exists_by_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Check if team exists by name."""
        stmt = select(Team.id).where(Team.name == name)
        if exclude_id:
            stmt = stmt.where(Team.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
