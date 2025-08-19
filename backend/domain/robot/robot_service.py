"""
Robot service for business logic operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from models import Robot
from schemas import RobotCreate, RobotUpdate, RobotResponse
from domain.robot.robot_repository import RobotRepository
from domain.robot.robot_validator import RobotValidator
from domain.shared.repository import BaseService


class RobotService(BaseService):
    """Service for robot business logic operations."""
    
    def __init__(self, repository: RobotRepository, validator: RobotValidator):
        super().__init__(repository)
        self.validator = validator
    
    async def create_robot(self, robot_data: RobotCreate) -> Robot:
        """
        Create a new robot.
        
        Args:
            robot_data: Robot creation data
            
        Returns:
            Created robot
            
        Raises:
            ValueError: If validation fails
        """
        # Validate robot data
        validation_result = self.validator.validate_robot_data(robot_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid robot data: {validation_result.errors}")
        
        # Check if robot name is unique within the team
        name_validation = await self.validator.validate_robot_name_unique(
            robot_data.name, robot_data.team_id if hasattr(robot_data, 'team_id') else 0
        )
        if not name_validation.is_valid:
            raise ValueError(f"Robot name validation failed: {name_validation.errors}")
        
        # Create robot
        robot = Robot(
            name=robot_data.name,
            robot_class_id=robot_data.robot_class_id,
            team_id=robot_data.team_id if hasattr(robot_data, 'team_id') else 0,
            waitlist=robot_data.waitlist if hasattr(robot_data, 'waitlist') else False,
            fee_paid=robot_data.fee_paid if hasattr(robot_data, 'fee_paid') else False,
            comments=robot_data.comments,
            created_at=datetime.utcnow()
        )
        
        return await self.repository.save(robot)
    
    async def get_robot(self, robot_id: int) -> Optional[Robot]:
        """
        Get robot by ID.
        
        Args:
            robot_id: Robot ID
            
        Returns:
            Robot or None if not found
        """
        return await self.repository.find_by_id(robot_id)
    
    async def get_robots(self, **filters) -> List[Robot]:
        """
        Get robots with optional filters.
        
        Args:
            **filters: Optional filters (team_id, robot_class_id, waitlist, fee_paid)
            
        Returns:
            List of robots
        """
        return await self.repository.find_all(**filters)
    
    async def get_robots_by_team(self, team_id: int) -> List[Robot]:
        """
        Get all robots for a specific team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of robots
        """
        return await self.repository.find_by_team(team_id)
    
    async def get_robots_by_class(self, robot_class_id: int) -> List[Robot]:
        """
        Get all robots in a specific robot class.
        
        Args:
            robot_class_id: Robot class ID
            
        Returns:
            List of robots
        """
        return await self.repository.find_by_robot_class(robot_class_id)
    
    async def get_waitlisted_robots(self, robot_class_id: Optional[int] = None) -> List[Robot]:
        """
        Get all robots on the waitlist.
        
        Args:
            robot_class_id: Optional robot class filter
            
        Returns:
            List of waitlisted robots
        """
        return await self.repository.find_waitlisted(robot_class_id)
    
    async def get_unpaid_robots(self, robot_class_id: Optional[int] = None) -> List[Robot]:
        """
        Get all robots with unpaid fees.
        
        Args:
            robot_class_id: Optional robot class filter
            
        Returns:
            List of robots with unpaid fees
        """
        return await self.repository.find_unpaid(robot_class_id)
    
    async def update_robot(self, robot_id: int, robot_data: RobotUpdate) -> Optional[Robot]:
        """
        Update robot.
        
        Args:
            robot_id: Robot ID
            robot_data: Robot update data
            
        Returns:
            Updated robot or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        # Check if robot exists
        robot = await self.repository.find_by_id(robot_id)
        if not robot:
            return None
        
        # Validate update data
        validation_result = self.validator.validate_robot_update(robot_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid robot update data: {validation_result.errors}")
        
        # Check name uniqueness if name is being updated
        if robot_data.name and robot_data.name != robot.name:
            name_validation = await self.validator.validate_robot_name_unique(
                robot_data.name, robot.team_id, robot_id
            )
            if not name_validation.is_valid:
                raise ValueError(f"Robot name validation failed: {name_validation.errors}")
        
        # Update robot fields
        if robot_data.name is not None:
            robot.name = robot_data.name
        if robot_data.robot_class_id is not None:
            robot.robot_class_id = robot_data.robot_class_id
        if robot_data.waitlist is not None:
            robot.waitlist = robot_data.waitlist
        if robot_data.fee_paid is not None:
            robot.fee_paid = robot_data.fee_paid
        if robot_data.comments is not None:
            robot.comments = robot_data.comments
        
        return await self.repository.save(robot)
    
    async def delete_robot(self, robot_id: int) -> bool:
        """
        Delete robot.
        
        Args:
            robot_id: Robot ID
            
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(robot_id)
    
    async def move_from_waitlist(self, robot_id: int) -> Optional[Robot]:
        """
        Move robot from waitlist to active status.
        
        Args:
            robot_id: Robot ID
            
        Returns:
            Updated robot or None if not found
        """
        robot = await self.repository.find_by_id(robot_id)
        if not robot or not robot.waitlist:
            return robot
        
        robot.waitlist = False
        return await self.repository.save(robot)
    
    async def mark_fee_paid(self, robot_id: int) -> Optional[Robot]:
        """
        Mark robot fee as paid.
        
        Args:
            robot_id: Robot ID
            
        Returns:
            Updated robot or None if not found
        """
        robot = await self.repository.find_by_id(robot_id)
        if not robot:
            return None
        
        robot.fee_paid = True
        return await self.repository.save(robot)
    
    async def change_robot_class(self, robot_id: int, new_class_id: int) -> Optional[Robot]:
        """
        Change robot's class.
        
        Args:
            robot_id: Robot ID
            new_class_id: New robot class ID
            
        Returns:
            Updated robot or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        robot = await self.repository.find_by_id(robot_id)
        if not robot:
            return None
        
        # Validate class change
        validation_result = self.validator.validate_robot_class_change(
            robot.robot_class_id, new_class_id
        )
        if not validation_result.is_valid:
            raise ValueError(f"Robot class change validation failed: {validation_result.errors}")
        
        robot.robot_class_id = new_class_id
        return await self.repository.save(robot)
    
    async def get_robot_statistics(self, robot_class_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get robot statistics.
        
        Args:
            robot_class_id: Optional robot class filter
            
        Returns:
            Dictionary with robot statistics
        """
        filters = {}
        if robot_class_id:
            filters["robot_class_id"] = robot_class_id
        
        all_robots = await self.repository.find_all(**filters)
        waitlisted = await self.repository.find_waitlisted(robot_class_id)
        unpaid = await self.repository.find_unpaid(robot_class_id)
        
        return {
            "total_robots": len(all_robots),
            "active_robots": len([r for r in all_robots if not r.waitlist]),
            "waitlisted_robots": len(waitlisted),
            "paid_robots": len([r for r in all_robots if r.fee_paid]),
            "unpaid_robots": len(unpaid)
        }
