"""
Robot validation logic.
"""
from typing import List

from domain.shared.repository import BaseRepository
from domain.validation.validation_result import ValidationResult
from schemas import RobotCreate, RobotUpdate


class RobotValidator:
    """Validator for robot-related operations."""
    
    def __init__(self, robot_repository: BaseRepository = None):
        self.robot_repository = robot_repository
    
    def validate_robot_data(self, data: RobotCreate) -> ValidationResult:
        """
        Validate robot creation data.
        
        Args:
            data: Robot creation data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate name
        if not data.name or not data.name.strip():
            errors.append("Robot name is required")
        elif len(data.name.strip()) > 100:
            errors.append("Robot name must be 100 characters or less")
        
        # Validate robot class ID
        if data.robot_class_id <= 0:
            errors.append("Valid robot class ID is required")
        
        # Validate comments
        if data.comments and len(data.comments) > 1000:
            errors.append("Robot comments must be 1000 characters or less")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_robot_update(self, data: RobotUpdate) -> ValidationResult:
        """
        Validate robot update data.
        
        Args:
            data: Robot update data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate name (if provided)
        if data.name is not None:
            if not data.name.strip():
                errors.append("Robot name cannot be empty")
            elif len(data.name.strip()) > 100:
                errors.append("Robot name must be 100 characters or less")
        
        # Validate robot class ID (if provided)
        if data.robot_class_id is not None and data.robot_class_id <= 0:
            errors.append("Valid robot class ID is required")
        
        # Validate comments (if provided)
        if data.comments is not None and len(data.comments) > 1000:
            errors.append("Robot comments must be 1000 characters or less")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    async def validate_robot_name_unique(self, name: str, team_id: int, exclude_id: int = None) -> ValidationResult:
        """Validate that robot name is unique within the team."""
        if not self.robot_repository:
            return ValidationResult(is_valid=True, errors=[])
        
        exists = await self.robot_repository.exists_by_name(name, team_id, exclude_id)
        if exists:
            return ValidationResult(
                is_valid=False,
                errors=[f"Robot with name '{name}' already exists in this team"]
            )
        
        return ValidationResult(is_valid=True, errors=[])
    
    async def validate_robot_exists(self, robot_id: int) -> ValidationResult:
        """Validate that robot exists."""
        if not self.robot_repository:
            return ValidationResult(is_valid=True, errors=[])
        
        exists = await self.robot_repository.exists(robot_id)
        if not exists:
            return ValidationResult(
                is_valid=False,
                errors=["Robot not found"]
            )
        
        return ValidationResult(is_valid=True, errors=[])
    
    def validate_robot_class_change(self, current_class_id: int, new_class_id: int) -> ValidationResult:
        """Validate robot class change."""
        errors = []
        
        if current_class_id == new_class_id:
            errors.append("Robot is already in this class")
        
        # Additional validation could include checking if matches exist
        # that would be affected by the class change
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_waitlist_status(self, waitlist: bool, fee_paid: bool) -> ValidationResult:
        """Validate waitlist and fee payment status combination."""
        errors = []
        
        # Business rule: robots on waitlist typically shouldn't have paid fees yet
        if waitlist and fee_paid:
            # This might be a warning rather than an error in some cases
            pass  # Allow this combination for flexibility
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
