"""
Player validation logic.
"""
from typing import List

from domain.shared.repository import BaseRepository
from domain.validation.validation_result import ValidationResult
from schemas import PlayerCreate, PlayerUpdate


class PlayerValidator:
    """Validator for player-related operations."""
    
    def __init__(self, player_repository: BaseRepository = None):
        self.player_repository = player_repository
    
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
    
    async def validate_player_name_unique(self, first_name: str, last_name: str, team_id: int, exclude_id: int = None) -> ValidationResult:
        """Validate that player name is unique within the team."""
        if not self.player_repository:
            return ValidationResult(is_valid=True, errors=[])
        
        exists = await self.player_repository.exists_by_name(first_name, last_name, team_id, exclude_id)
        if exists:
            return ValidationResult(
                is_valid=False,
                errors=[f"Player '{first_name} {last_name}' already exists in this team"]
            )
        
        return ValidationResult(is_valid=True, errors=[])
    
    async def validate_player_email_unique(self, email: str, exclude_id: int = None) -> ValidationResult:
        """Validate that player email is unique."""
        if not email or not self.player_repository:
            return ValidationResult(is_valid=True, errors=[])
        
        exists = await self.player_repository.exists_by_email(email, exclude_id)
        if exists:
            return ValidationResult(
                is_valid=False,
                errors=[f"Player with email '{email}' already exists"]
            )
        
        return ValidationResult(is_valid=True, errors=[])
    
    async def validate_player_exists(self, player_id: int) -> ValidationResult:
        """Validate that player exists."""
        if not self.player_repository:
            return ValidationResult(is_valid=True, errors=[])
        
        exists = await self.player_repository.exists(player_id)
        if not exists:
            return ValidationResult(
                is_valid=False,
                errors=["Player not found"]
            )
        
        return ValidationResult(is_valid=True, errors=[])
    
    def validate_email_format(self, email: str) -> ValidationResult:
        """Validate email format."""
        errors = []
        
        if not email:
            return ValidationResult(is_valid=True, errors=[])
        
        # Basic email validation
        if '@' not in email:
            errors.append("Email must contain @ symbol")
        elif email.count('@') > 1:
            errors.append("Email must contain only one @ symbol")
        elif '.' not in email.split('@')[-1]:
            errors.append("Email domain must contain a dot")
        elif len(email) > 255:
            errors.append("Email must be 255 characters or less")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
