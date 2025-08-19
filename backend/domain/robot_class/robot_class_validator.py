"""
Robot class validation logic.
"""
from typing import List

from domain.shared.repository import BaseRepository
from domain.validation.validation_result import ValidationResult
from schemas import RobotClassCreate, RobotClassUpdate


class RobotClassValidator:
    """Validator for robot class-related operations."""
    
    def __init__(self, robot_class_repository: BaseRepository = None):
        self.robot_class_repository = robot_class_repository
    
    def validate_robot_class_data(self, data: RobotClassCreate) -> ValidationResult:
        """
        Validate robot class creation data.
        
        Args:
            data: Robot class creation data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate name
        if not data.name or not data.name.strip():
            errors.append("Robot class name is required")
        elif len(data.name.strip()) > 100:
            errors.append("Robot class name must be 100 characters or less")
        
        # Validate weight limit
        if data.weight_limit <= 0:
            errors.append("Weight limit must be greater than 0")
        elif data.weight_limit > 100000:  # 100kg in grams
            errors.append("Weight limit cannot exceed 100,000 grams")
        
        # Validate match duration
        if data.match_duration <= 0:
            errors.append("Match duration must be greater than 0 seconds")
        elif data.match_duration > 600:  # 10 minutes
            errors.append("Match duration cannot exceed 600 seconds")
        
        # Validate pit activation time
        if data.pit_activation_time < 0:
            errors.append("Pit activation time cannot be negative")
        elif data.pit_activation_time >= data.match_duration:
            errors.append("Pit activation time must be less than match duration")
        
        # Validate button delay (if provided)
        if data.button_delay is not None:
            if data.button_delay < 0:
                errors.append("Button delay cannot be negative")
            elif data.button_delay >= data.match_duration:
                errors.append("Button delay must be less than match duration")
        
        # Validate button duration (if provided)
        if data.button_duration is not None:
            if data.button_duration <= 0:
                errors.append("Button duration must be greater than 0 seconds")
            elif data.button_delay is not None and (data.button_delay + data.button_duration) > data.match_duration:
                errors.append("Button delay + duration cannot exceed match duration")
        
        # Validate description length
        if data.description and len(data.description) > 1000:
            errors.append("Robot class description must be 1000 characters or less")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_robot_class_update(self, data: RobotClassUpdate) -> ValidationResult:
        """
        Validate robot class update data.
        
        Args:
            data: Robot class update data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate name (if provided)
        if data.name is not None:
            if not data.name.strip():
                errors.append("Robot class name cannot be empty")
            elif len(data.name.strip()) > 100:
                errors.append("Robot class name must be 100 characters or less")
        
        # Validate weight limit (if provided)
        if data.weight_limit is not None:
            if data.weight_limit <= 0:
                errors.append("Weight limit must be greater than 0")
            elif data.weight_limit > 100000:  # 100kg in grams
                errors.append("Weight limit cannot exceed 100,000 grams")
        
        # Validate match duration (if provided)
        if data.match_duration is not None:
            if data.match_duration <= 0:
                errors.append("Match duration must be greater than 0 seconds")
            elif data.match_duration > 600:  # 10 minutes
                errors.append("Match duration cannot exceed 600 seconds")
        
        # Validate pit activation time (if provided)
        if data.pit_activation_time is not None:
            if data.pit_activation_time < 0:
                errors.append("Pit activation time cannot be negative")
            # Note: We can't validate against match_duration here without the current values
        
        # Validate button delay (if provided)
        if data.button_delay is not None and data.button_delay < 0:
            errors.append("Button delay cannot be negative")
        
        # Validate button duration (if provided)
        if data.button_duration is not None and data.button_duration <= 0:
            errors.append("Button duration must be greater than 0 seconds")
        
        # Validate description length (if provided)
        if data.description is not None and len(data.description) > 1000:
            errors.append("Robot class description must be 1000 characters or less")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    async def validate_robot_class_name_unique(self, name: str, exclude_id: int = None) -> ValidationResult:
        """Validate that robot class name is unique."""
        if not self.robot_class_repository:
            return ValidationResult(is_valid=True, errors=[])
        
        exists = await self.robot_class_repository.exists_by_name(name, exclude_id)
        if exists:
            return ValidationResult(
                is_valid=False,
                errors=[f"Robot class with name '{name}' already exists"]
            )
        
        return ValidationResult(is_valid=True, errors=[])
    
    async def validate_robot_class_exists(self, robot_class_id: int) -> ValidationResult:
        """Validate that robot class exists."""
        if not self.robot_class_repository:
            return ValidationResult(is_valid=True, errors=[])
        
        exists = await self.robot_class_repository.exists(robot_class_id)
        if not exists:
            return ValidationResult(
                is_valid=False,
                errors=["Robot class not found"]
            )
        
        return ValidationResult(is_valid=True, errors=[])
    
    async def validate_robot_class_deletion(self, robot_class_id: int) -> ValidationResult:
        """Validate that robot class can be deleted."""
        if not self.robot_class_repository:
            return ValidationResult(is_valid=True, errors=[])
        
        robot_count = await self.robot_class_repository.count_robots_in_class(robot_class_id)
        if robot_count > 0:
            return ValidationResult(
                is_valid=False,
                errors=[f"Cannot delete robot class with {robot_count} active robots"]
            )
        
        return ValidationResult(is_valid=True, errors=[])
    
    def validate_hazard_timing(self, match_duration: int, pit_activation_time: int, 
                              button_delay: int = None, button_duration: int = None) -> ValidationResult:
        """Validate hazard timing configuration."""
        errors = []
        
        # Validate pit activation time
        if pit_activation_time >= match_duration:
            errors.append("Pit activation time must be less than match duration")
        
        # Validate button timing if provided
        if button_delay is not None:
            if button_delay >= match_duration:
                errors.append("Button delay must be less than match duration")
            
            if button_duration is not None:
                if (button_delay + button_duration) > match_duration:
                    errors.append("Button delay + duration cannot exceed match duration")
                
                # Check that button doesn't interfere with pit activation
                if button_delay <= pit_activation_time <= (button_delay + button_duration):
                    errors.append("Button activation period cannot overlap with pit activation time")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
