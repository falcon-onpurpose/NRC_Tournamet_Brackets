"""
Player validation logic.
"""
from typing import List

from domain.validation.validation_result import ValidationResult
from schemas import PlayerCreate, PlayerUpdate


class PlayerValidator:
    """Validator for player-related operations."""
    
    def validate_player_data(self, data: PlayerCreate) -> ValidationResult:
        """
        Validate player creation data.
        
        Args:
            data: Player creation data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate first name
        if not data.first_name or not data.first_name.strip():
            errors.append("Player first name is required")
        elif len(data.first_name.strip()) > 50:
            errors.append("Player first name must be 50 characters or less")
        
        # Validate last name
        if not data.last_name or not data.last_name.strip():
            errors.append("Player last name is required")
        elif len(data.last_name.strip()) > 50:
            errors.append("Player last name must be 50 characters or less")
        
        # Validate email
        if data.email:
            if len(data.email) > 255:
                errors.append("Player email must be 255 characters or less")
            elif '@' not in data.email:
                errors.append("Player email must be a valid email address")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_player_update(self, data: PlayerUpdate) -> ValidationResult:
        """
        Validate player update data.
        
        Args:
            data: Player update data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate first name (if provided)
        if data.first_name is not None:
            if not data.first_name.strip():
                errors.append("Player first name cannot be empty")
            elif len(data.first_name.strip()) > 50:
                errors.append("Player first name must be 50 characters or less")
        
        # Validate last name (if provided)
        if data.last_name is not None:
            if not data.last_name.strip():
                errors.append("Player last name cannot be empty")
            elif len(data.last_name.strip()) > 50:
                errors.append("Player last name must be 50 characters or less")
        
        # Validate email (if provided)
        if data.email is not None:
            if data.email and len(data.email) > 255:
                errors.append("Player email must be 255 characters or less")
            elif data.email and '@' not in data.email:
                errors.append("Player email must be a valid email address")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_player_exists(self, player_id: int) -> ValidationResult:
        """Validate that player exists."""
        if player_id <= 0:
            return ValidationResult(
                is_valid=False,
                errors=["Invalid player ID"]
            )
        return ValidationResult(is_valid=True, errors=[])
