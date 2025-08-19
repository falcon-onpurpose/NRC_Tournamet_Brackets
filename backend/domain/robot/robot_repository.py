"""
Robot repository for data access operations.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from models import Robot
from domain.shared.repository import BaseRepository


class RobotRepository(BaseRepository[Robot]):
    """Repository for robot data access operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def find_by_id(self, robot_id: int) -> Optional[Robot]:
        """Find robot by ID with relationships loaded."""
        query = (
            select(Robot)
            .options(
                selectinload(Robot.team),
                selectinload(Robot.robot_class)
            )
            .where(Robot.id == robot_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def find_all(self, **filters) -> List[Robot]:
        """Find all robots with optional filters."""
        query = (
            select(Robot)
            .options(
                selectinload(Robot.team),
                selectinload(Robot.robot_class)
            )
        )
        
        # Apply filters
        if "team_id" in filters:
            query = query.where(Robot.team_id == filters["team_id"])
        if "robot_class_id" in filters:
            query = query.where(Robot.robot_class_id == filters["robot_class_id"])
        if "waitlist" in filters:
            query = query.where(Robot.waitlist == filters["waitlist"])
        if "fee_paid" in filters:
            query = query.where(Robot.fee_paid == filters["fee_paid"])
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def find_by_team(self, team_id: int) -> List[Robot]:
        """Find all robots for a specific team."""
        query = (
            select(Robot)
            .options(
                selectinload(Robot.team),
                selectinload(Robot.robot_class)
            )
            .where(Robot.team_id == team_id)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def find_by_robot_class(self, robot_class_id: int) -> List[Robot]:
        """Find all robots in a specific robot class."""
        query = (
            select(Robot)
            .options(
                selectinload(Robot.team),
                selectinload(Robot.robot_class)
            )
            .where(Robot.robot_class_id == robot_class_id)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def find_by_name(self, name: str, team_id: Optional[int] = None) -> Optional[Robot]:
        """Find robot by name, optionally within a specific team."""
        query = select(Robot).where(Robot.name == name)
        
        if team_id:
            query = query.where(Robot.team_id == team_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def find_waitlisted(self, robot_class_id: Optional[int] = None) -> List[Robot]:
        """Find all robots on the waitlist."""
        query = (
            select(Robot)
            .options(
                selectinload(Robot.team),
                selectinload(Robot.robot_class)
            )
            .where(Robot.waitlist == True)
        )
        
        if robot_class_id:
            query = query.where(Robot.robot_class_id == robot_class_id)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def find_unpaid(self, robot_class_id: Optional[int] = None) -> List[Robot]:
        """Find all robots with unpaid fees."""
        query = (
            select(Robot)
            .options(
                selectinload(Robot.team),
                selectinload(Robot.robot_class)
            )
            .where(Robot.fee_paid == False)
        )
        
        if robot_class_id:
            query = query.where(Robot.robot_class_id == robot_class_id)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def save(self, robot: Robot) -> Robot:
        """Save robot (create or update)."""
        if robot.id is None:
            # Creating new robot
            self.session.add(robot)
        else:
            # Updating existing robot
            await self.session.merge(robot)
        
        await self.session.commit()
        await self.session.refresh(robot)
        return robot
    
    async def delete(self, robot_id: int) -> bool:
        """Delete robot by ID."""
        robot = await self.find_by_id(robot_id)
        if robot:
            await self.session.delete(robot)
            await self.session.commit()
            return True
        return False
    
    async def exists(self, robot_id: int) -> bool:
        """Check if robot exists."""
        query = select(Robot.id).where(Robot.id == robot_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_name(self, name: str, team_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if robot name exists within a team."""
        query = select(Robot.id).where(
            and_(Robot.name == name, Robot.team_id == team_id)
        )
        
        if exclude_id:
            query = query.where(Robot.id != exclude_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def count_by_robot_class(self, robot_class_id: int) -> int:
        """Count robots in a specific robot class."""
        from sqlalchemy import func
        query = select(func.count(Robot.id)).where(Robot.robot_class_id == robot_class_id)
        result = await self.session.execute(query)
        return result.scalar() or 0
