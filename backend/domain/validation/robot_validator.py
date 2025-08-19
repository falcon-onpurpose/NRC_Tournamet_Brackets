"""
Robot validation logic.
"""
from typing import List

from domain.validation.validation_result import ValidationResult
from schemas import RobotCreate, RobotUpdate


class RobotValidator:
    """Validator for robot-related operations."""
    
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
    
    def validate_robot_exists(self, robot_id: int) -> ValidationResult:
        """Validate that robot exists."""
        if robot_id <= 0:
            return ValidationResult(
                is_valid=False,
                errors=["Invalid robot ID"]
            )
        return ValidationResult(is_valid=True, errors=[])
