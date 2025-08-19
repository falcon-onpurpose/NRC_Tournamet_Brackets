"""
Team validation logic for the validation domain.
"""
from typing import List

from domain.validation.validation_result import ValidationResult
from schemas import TeamCreate, TeamUpdate


class TeamValidator:
    """Validator for team-related operations in validation domain."""
    
    def validate_team_data(self, data: TeamCreate) -> ValidationResult:
        """
        Validate team creation data.
        
        Args:
            data: Team creation data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate name
        if not data.name or not data.name.strip():
            errors.append("Team name is required")
        elif len(data.name.strip()) > 100:
            errors.append("Team name must be 100 characters or less")
        
        # Validate tournament ID
        if data.tournament_id <= 0:
            errors.append("Valid tournament ID is required")
        
        # Validate email (optional)
        if data.email:
            if len(data.email) > 255:
                errors.append("Team email must be 255 characters or less")
            elif '@' not in data.email:
                errors.append("Team email must be a valid email address")
        
        # Validate phone (optional)
        if data.phone and len(data.phone) > 20:
            errors.append("Team phone must be 20 characters or less")
        
        # Validate address (optional)
        if data.address and len(data.address) > 500:
            errors.append("Team address must be 500 characters or less")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_team_update(self, data: TeamUpdate) -> ValidationResult:
        """
        Validate team update data.
        
        Args:
            data: Team update data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate name (if provided)
        if data.name is not None:
            if not data.name.strip():
                errors.append("Team name cannot be empty")
            elif len(data.name.strip()) > 100:
                errors.append("Team name must be 100 characters or less")
        
        # Validate email (if provided)
        if data.email is not None:
            if data.email and len(data.email) > 255:
                errors.append("Team email must be 255 characters or less")
            elif data.email and '@' not in data.email:
                errors.append("Team email must be a valid email address")
        
        # Validate phone (if provided)
        if data.phone is not None and data.phone and len(data.phone) > 20:
            errors.append("Team phone must be 20 characters or less")
        
        # Validate address (if provided)
        if data.address is not None and data.address and len(data.address) > 500:
            errors.append("Team address must be 500 characters or less")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
