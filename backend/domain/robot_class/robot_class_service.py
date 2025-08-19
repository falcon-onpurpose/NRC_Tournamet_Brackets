"""
Robot class service for business logic operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from models import RobotClass
from schemas import RobotClassCreate, RobotClassUpdate, RobotClassResponse
from domain.robot_class.robot_class_repository import RobotClassRepository
from domain.robot_class.robot_class_validator import RobotClassValidator
from domain.shared.repository import BaseService


class RobotClassService(BaseService):
    """Service for robot class business logic operations."""
    
    def __init__(self, repository: RobotClassRepository, validator: RobotClassValidator):
        super().__init__(repository)
        self.validator = validator
    
    async def create_robot_class(self, robot_class_data: RobotClassCreate) -> RobotClass:
        """
        Create a new robot class.
        
        Args:
            robot_class_data: Robot class creation data
            
        Returns:
            Created robot class
            
        Raises:
            ValueError: If validation fails
        """
        # Validate robot class data
        validation_result = self.validator.validate_robot_class_data(robot_class_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid robot class data: {validation_result.errors}")
        
        # Check if robot class name is unique
        name_validation = await self.validator.validate_robot_class_name_unique(robot_class_data.name)
        if not name_validation.is_valid:
            raise ValueError(f"Robot class name validation failed: {name_validation.errors}")
        
        # Validate hazard timing
        timing_validation = self.validator.validate_hazard_timing(
            robot_class_data.match_duration,
            robot_class_data.pit_activation_time,
            robot_class_data.button_delay,
            robot_class_data.button_duration
        )
        if not timing_validation.is_valid:
            raise ValueError(f"Hazard timing validation failed: {timing_validation.errors}")
        
        # Create robot class
        robot_class = RobotClass(
            name=robot_class_data.name,
            weight_limit=robot_class_data.weight_limit,
            match_duration=robot_class_data.match_duration,
            pit_activation_time=robot_class_data.pit_activation_time,
            button_delay=robot_class_data.button_delay,
            button_duration=robot_class_data.button_duration,
            description=robot_class_data.description,
            created_at=datetime.utcnow()
        )
        
        return await self.repository.save(robot_class)
    
    async def get_robot_class(self, robot_class_id: int) -> Optional[RobotClass]:
        """
        Get robot class by ID.
        
        Args:
            robot_class_id: Robot class ID
            
        Returns:
            Robot class or None if not found
        """
        return await self.repository.find_by_id(robot_class_id)
    
    async def get_robot_classes(self, **filters) -> List[RobotClass]:
        """
        Get robot classes with optional filters.
        
        Args:
            **filters: Optional filters (name, weight_limit, match_duration)
            
        Returns:
            List of robot classes
        """
        return await self.repository.find_all(**filters)
    
    async def get_robot_class_by_name(self, name: str) -> Optional[RobotClass]:
        """
        Get robot class by name.
        
        Args:
            name: Robot class name
            
        Returns:
            Robot class or None if not found
        """
        return await self.repository.find_by_name(name)
    
    async def get_robot_classes_by_weight_range(self, min_weight: int, max_weight: int) -> List[RobotClass]:
        """
        Get robot classes within a weight range.
        
        Args:
            min_weight: Minimum weight limit
            max_weight: Maximum weight limit
            
        Returns:
            List of robot classes
        """
        return await self.repository.find_by_weight_range(min_weight, max_weight)
    
    async def get_active_robot_classes(self) -> List[RobotClass]:
        """
        Get robot classes that have active robots.
        
        Returns:
            List of active robot classes
        """
        return await self.repository.find_active_classes()
    
    async def update_robot_class(self, robot_class_id: int, robot_class_data: RobotClassUpdate) -> Optional[RobotClass]:
        """
        Update robot class.
        
        Args:
            robot_class_id: Robot class ID
            robot_class_data: Robot class update data
            
        Returns:
            Updated robot class or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        # Check if robot class exists
        robot_class = await self.repository.find_by_id(robot_class_id)
        if not robot_class:
            return None
        
        # Validate update data
        validation_result = self.validator.validate_robot_class_update(robot_class_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid robot class update data: {validation_result.errors}")
        
        # Check name uniqueness if name is being updated
        if robot_class_data.name and robot_class_data.name != robot_class.name:
            name_validation = await self.validator.validate_robot_class_name_unique(
                robot_class_data.name, robot_class_id
            )
            if not name_validation.is_valid:
                raise ValueError(f"Robot class name validation failed: {name_validation.errors}")
        
        # Get current values for timing validation
        current_match_duration = robot_class_data.match_duration if robot_class_data.match_duration is not None else robot_class.match_duration
        current_pit_activation = robot_class_data.pit_activation_time if robot_class_data.pit_activation_time is not None else robot_class.pit_activation_time
        current_button_delay = robot_class_data.button_delay if robot_class_data.button_delay is not None else robot_class.button_delay
        current_button_duration = robot_class_data.button_duration if robot_class_data.button_duration is not None else robot_class.button_duration
        
        # Validate hazard timing with updated values
        timing_validation = self.validator.validate_hazard_timing(
            current_match_duration,
            current_pit_activation,
            current_button_delay,
            current_button_duration
        )
        if not timing_validation.is_valid:
            raise ValueError(f"Hazard timing validation failed: {timing_validation.errors}")
        
        # Update robot class fields
        if robot_class_data.name is not None:
            robot_class.name = robot_class_data.name
        if robot_class_data.weight_limit is not None:
            robot_class.weight_limit = robot_class_data.weight_limit
        if robot_class_data.match_duration is not None:
            robot_class.match_duration = robot_class_data.match_duration
        if robot_class_data.pit_activation_time is not None:
            robot_class.pit_activation_time = robot_class_data.pit_activation_time
        if robot_class_data.button_delay is not None:
            robot_class.button_delay = robot_class_data.button_delay
        if robot_class_data.button_duration is not None:
            robot_class.button_duration = robot_class_data.button_duration
        if robot_class_data.description is not None:
            robot_class.description = robot_class_data.description
        
        return await self.repository.save(robot_class)
    
    async def delete_robot_class(self, robot_class_id: int) -> bool:
        """
        Delete robot class.
        
        Args:
            robot_class_id: Robot class ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValueError: If robot class has active robots
        """
        # Validate that robot class can be deleted
        deletion_validation = await self.validator.validate_robot_class_deletion(robot_class_id)
        if not deletion_validation.is_valid:
            raise ValueError(f"Cannot delete robot class: {deletion_validation.errors}")
        
        return await self.repository.delete(robot_class_id)
    
    async def get_robot_class_statistics(self) -> Dict[str, Any]:
        """
        Get robot class statistics.
        
        Returns:
            Dictionary with robot class statistics
        """
        all_classes = await self.repository.find_all()
        active_classes = await self.repository.find_active_classes()
        usage_stats = await self.repository.get_class_usage_statistics()
        
        # Calculate weight distribution
        weight_ranges = {
            "under_1kg": 0,
            "1kg_to_5kg": 0,
            "5kg_to_15kg": 0,
            "over_15kg": 0
        }
        
        for robot_class in all_classes:
            weight_kg = robot_class.weight_limit / 1000
            if weight_kg < 1:
                weight_ranges["under_1kg"] += 1
            elif weight_kg <= 5:
                weight_ranges["1kg_to_5kg"] += 1
            elif weight_kg <= 15:
                weight_ranges["5kg_to_15kg"] += 1
            else:
                weight_ranges["over_15kg"] += 1
        
        return {
            "total_classes": len(all_classes),
            "active_classes": len(active_classes),
            "inactive_classes": len(all_classes) - len(active_classes),
            "weight_distribution": weight_ranges,
            "usage_statistics": usage_stats,
            "average_match_duration": sum(rc.match_duration for rc in all_classes) / len(all_classes) if all_classes else 0
        }
    
    async def get_robot_count_by_class(self, robot_class_id: int) -> int:
        """
        Get count of robots in a specific robot class.
        
        Args:
            robot_class_id: Robot class ID
            
        Returns:
            Number of robots in the class
        """
        return await self.repository.count_robots_in_class(robot_class_id)
