"""
Tournament validator for data validation operations.
"""
from typing import List
from datetime import datetime
from domain.validation.validation_result import ValidationResult
from schemas import TournamentCreate, TournamentUpdate


class TournamentValidator:
    """Validator for tournament data validation operations."""
    
    async def validate_tournament_create(self, data: TournamentCreate) -> ValidationResult:
        """Validate tournament creation data."""
        errors = []
        
        # Validate name
        if not data.name or len(data.name.strip()) == 0:
            errors.append("Tournament name is required")
        elif len(data.name) > 255:
            errors.append("Tournament name must be less than 255 characters")
        
        # Validate description
        if not data.description or len(data.description.strip()) == 0:
            errors.append("Tournament description is required")
        elif len(data.description) > 1000:
            errors.append("Tournament description must be less than 1000 characters")
        
        # Validate dates
        if not data.start_date:
            errors.append("Start date is required")
        if not data.end_date:
            errors.append("End date is required")
        
        if data.start_date and data.end_date:
            try:
                # Handle both string and datetime inputs
                if isinstance(data.start_date, str):
                    start_date = datetime.fromisoformat(data.start_date.replace('Z', '+00:00'))
                else:
                    start_date = data.start_date
                
                if isinstance(data.end_date, str):
                    end_date = datetime.fromisoformat(data.end_date.replace('Z', '+00:00'))
                else:
                    end_date = data.end_date
                
                if end_date <= start_date:
                    errors.append("End date must be after start date")
                
                if start_date < datetime.now():
                    errors.append("Start date cannot be in the past")
                    
            except ValueError:
                errors.append("Invalid date format")
        
        # Validate swiss rounds count
        if data.swiss_rounds_count < 1:
            errors.append("Swiss rounds count must be at least 1")
        elif data.swiss_rounds_count > 10:
            errors.append("Swiss rounds count cannot exceed 10")
        
        # Validate max teams
        if data.max_teams < 1:
            errors.append("Maximum teams must be at least 1")
        elif data.max_teams > 100:
            errors.append("Maximum teams cannot exceed 100")
        
        # Validate status
        valid_statuses = ["setup", "registration", "swiss_rounds", "elimination", "completed", "cancelled"]
        if data.status not in valid_statuses:
            errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    async def validate_tournament_update(self, data: TournamentUpdate) -> ValidationResult:
        """Validate tournament update data."""
        errors = []
        
        # Validate name if provided
        if data.name is not None:
            if len(data.name.strip()) == 0:
                errors.append("Tournament name cannot be empty")
            elif len(data.name) > 255:
                errors.append("Tournament name must be less than 255 characters")
        
        # Validate description if provided
        if data.description is not None:
            if len(data.description.strip()) == 0:
                errors.append("Tournament description cannot be empty")
            elif len(data.description) > 1000:
                errors.append("Tournament description must be less than 1000 characters")
        
        # Validate dates if provided
        if data.start_date is not None or data.end_date is not None:
            # This would need more complex validation if we're updating dates
            # For now, just validate format
            if data.start_date:
                try:
                    if isinstance(data.start_date, str):
                        datetime.fromisoformat(data.start_date.replace('Z', '+00:00'))
                except ValueError:
                    errors.append("Invalid start date format")
            
            if data.end_date:
                try:
                    if isinstance(data.end_date, str):
                        datetime.fromisoformat(data.end_date.replace('Z', '+00:00'))
                except ValueError:
                    errors.append("Invalid end date format")
        
        # Validate swiss rounds count if provided
        if data.swiss_rounds_count is not None:
            if data.swiss_rounds_count < 1:
                errors.append("Swiss rounds count must be at least 1")
            elif data.swiss_rounds_count > 10:
                errors.append("Swiss rounds count cannot exceed 10")
        
        # Validate max teams if provided
        if data.max_teams is not None:
            if data.max_teams < 1:
                errors.append("Maximum teams must be at least 1")
            elif data.max_teams > 100:
                errors.append("Maximum teams cannot exceed 100")
        
        # Validate status if provided
        if data.status is not None:
            valid_statuses = ["setup", "registration", "swiss_rounds", "elimination", "completed", "cancelled"]
            if data.status not in valid_statuses:
                errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
