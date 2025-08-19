"""
Robot class repository for data access operations.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import RobotClass
from domain.shared.repository import BaseRepository


class RobotClassRepository(BaseRepository[RobotClass]):
    """Repository for robot class data access operations."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def find_by_id(self, robot_class_id: int) -> Optional[RobotClass]:
        """Find robot class by ID with relationships loaded."""
        query = (
            select(RobotClass)
            .options(selectinload(RobotClass.robots))
            .where(RobotClass.id == robot_class_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def find_all(self, **filters) -> List[RobotClass]:
        """Find all robot classes with optional filters."""
        query = (
            select(RobotClass)
            .options(selectinload(RobotClass.robots))
        )
        
        # Apply filters
        if "name" in filters:
            query = query.where(RobotClass.name.ilike(f"%{filters['name']}%"))
        if "weight_limit" in filters:
            query = query.where(RobotClass.weight_limit == filters["weight_limit"])
        if "match_duration" in filters:
            query = query.where(RobotClass.match_duration == filters["match_duration"])
        
        # Order by weight limit for consistent ordering
        query = query.order_by(RobotClass.weight_limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def find_by_name(self, name: str) -> Optional[RobotClass]:
        """Find robot class by name."""
        query = select(RobotClass).where(RobotClass.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def find_by_weight_range(self, min_weight: int, max_weight: int) -> List[RobotClass]:
        """Find robot classes within a weight range."""
        query = (
            select(RobotClass)
            .options(selectinload(RobotClass.robots))
            .where(
                RobotClass.weight_limit >= min_weight,
                RobotClass.weight_limit <= max_weight
            )
            .order_by(RobotClass.weight_limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def find_active_classes(self) -> List[RobotClass]:
        """Find robot classes that have active robots."""
        query = (
            select(RobotClass)
            .options(selectinload(RobotClass.robots))
            .join(RobotClass.robots)
            .where(RobotClass.robots.any())
            .order_by(RobotClass.weight_limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def save(self, robot_class: RobotClass) -> RobotClass:
        """Save robot class (create or update)."""
        if robot_class.id is None:
            # Creating new robot class
            self.session.add(robot_class)
        else:
            # Updating existing robot class
            await self.session.merge(robot_class)
        
        await self.session.commit()
        await self.session.refresh(robot_class)
        return robot_class
    
    async def delete(self, robot_class_id: int) -> bool:
        """Delete robot class by ID."""
        robot_class = await self.find_by_id(robot_class_id)
        if robot_class:
            await self.session.delete(robot_class)
            await self.session.commit()
            return True
        return False
    
    async def exists(self, robot_class_id: int) -> bool:
        """Check if robot class exists."""
        query = select(RobotClass.id).where(RobotClass.id == robot_class_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Check if robot class name exists."""
        query = select(RobotClass.id).where(RobotClass.name == name)
        
        if exclude_id:
            query = query.where(RobotClass.id != exclude_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def count_robots_in_class(self, robot_class_id: int) -> int:
        """Count robots in a specific robot class."""
        from sqlalchemy import func
        from models import Robot
        
        query = select(func.count(Robot.id)).where(Robot.robot_class_id == robot_class_id)
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def get_class_usage_statistics(self) -> List[dict]:
        """Get usage statistics for all robot classes."""
        from sqlalchemy import func
        from models import Robot
        
        query = (
            select(
                RobotClass.id,
                RobotClass.name,
                RobotClass.weight_limit,
                func.count(Robot.id).label('robot_count')
            )
            .outerjoin(Robot, RobotClass.id == Robot.robot_class_id)
            .group_by(RobotClass.id, RobotClass.name, RobotClass.weight_limit)
            .order_by(RobotClass.weight_limit)
        )
        
        result = await self.session.execute(query)
        return [
            {
                "id": row.id,
                "name": row.name,
                "weight_limit": row.weight_limit,
                "robot_count": row.robot_count
            }
            for row in result
        ]
