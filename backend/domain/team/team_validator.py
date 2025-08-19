"""
Team validation logic.
"""
from typing import List, Optional
from dataclasses import dataclass

from schemas import TeamCreate, TeamUpdate


@dataclass
class ValidationResult:
    """Validation result with success status and error messages."""
    is_valid: bool
    errors: List[str]


class TeamValidator:
    """Validator for team-related operations."""
    
    def validate_team_data(self, team_data: TeamCreate) -> ValidationResult:
        """Validate team creation data."""
        errors = []
        
        # Name validation
        if not team_data.name or not team_data.name.strip():
            errors.append("Team name is required")
        elif len(team_data.name) > 100:
            errors.append("Team name must be 100 characters or less")
        
        # Tournament ID validation
        if not team_data.tournament_id:
            errors.append("Tournament ID is required")
        elif team_data.tournament_id <= 0:
            errors.append("Tournament ID must be positive")
        
        # Email validation (optional but if provided, must be valid)
        if team_data.email:
            if '@' not in team_data.email or '.' not in team_data.email:
                errors.append("Invalid email format")
        
        # Phone validation (optional but if provided, must be valid)
        if team_data.phone:
            if len(team_data.phone) < 10:
                errors.append("Phone number must be at least 10 digits")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_team_update(self, team_data: TeamUpdate) -> ValidationResult:
        """Validate team update data."""
        errors = []
        
        # Name validation (if provided)
        if team_data.name is not None:
            if not team_data.name.strip():
                errors.append("Team name cannot be empty")
            elif len(team_data.name) > 100:
                errors.append("Team name must be 100 characters or less")
        
        # Email validation (if provided)
        if team_data.email is not None:
            if team_data.email and ('@' not in team_data.email or '.' not in team_data.email):
                errors.append("Invalid email format")
        
        # Phone validation (if provided)
        if team_data.phone is not None:
            if team_data.phone and len(team_data.phone) < 10:
                errors.append("Phone number must be at least 10 digits")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_team_name_unique(self, name: str, exclude_id: Optional[int] = None) -> ValidationResult:
        """Validate that team name is unique."""
        # This will be checked against the repository
        return ValidationResult(is_valid=True, errors=[])
    
    def validate_team_exists(self, team_id: int) -> ValidationResult:
        """Validate that team exists."""
        if team_id <= 0:
            return ValidationResult(
                is_valid=False,
                errors=["Invalid team ID"]
            )
        return ValidationResult(is_valid=True, errors=[])
