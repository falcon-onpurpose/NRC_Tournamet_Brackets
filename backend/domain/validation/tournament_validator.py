"""
Tournament validation logic.
"""
from typing import List
from datetime import datetime

from domain.validation.validation_result import ValidationResult
from schemas import TournamentCreate, TournamentUpdate


class TournamentValidator:
    """Validator for tournament-related operations."""
    
    def __init__(self):
        self.valid_tournament_formats = [
            "single_elimination",
            "double_elimination", 
            "swiss",
            "round_robin",
            "hybrid_swiss_elimination"
        ]
        
        self.valid_tournament_statuses = [
            "setup",
            "active",
            "running",
            "paused",
            "completed",
            "cancelled"
        ]
    
    def validate_tournament_data(self, data: TournamentCreate) -> ValidationResult:
        """
        Validate tournament creation data.
        
        Args:
            data: Tournament creation data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate name
        if not data.name or not data.name.strip():
            errors.append("Tournament name is required")
        elif len(data.name.strip()) > 255:
            errors.append("Tournament name must be 255 characters or less")
        
        # Validate format
        if hasattr(data, 'format') and data.format not in self.valid_tournament_formats:
            errors.append(f"Invalid tournament format. Must be one of: {', '.join(self.valid_tournament_formats)}")
        
        # Validate location
        if not data.location or not data.location.strip():
            errors.append("Tournament location is required")
        elif len(data.location.strip()) > 255:
            errors.append("Tournament location must be 255 characters or less")
        
        # Validate description
        if data.description and len(data.description) > 1000:
            errors.append("Tournament description must be 1000 characters or less")
        
        # Validate Swiss rounds
        if hasattr(data, 'format') and data.format in ["swiss", "hybrid_swiss_elimination"]:
            if hasattr(data, 'swiss_rounds_count'):
                if data.swiss_rounds_count < 1:
                    errors.append("Swiss rounds must be at least 1")
                elif data.swiss_rounds_count > 20:
                    errors.append("Swiss rounds cannot exceed 20")
        
        # Validate dates
        if data.start_date and data.end_date:
            if data.start_date >= data.end_date:
                errors.append("Start date must be before end date")
        
        if data.start_date and data.start_date < datetime.utcnow():
            errors.append("Start date cannot be in the past")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_tournament_update(self, data: TournamentUpdate) -> ValidationResult:
        """
        Validate tournament update data.
        
        Args:
            data: Tournament update data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate name (if provided)
        if data.name is not None:
            if not data.name.strip():
                errors.append("Tournament name cannot be empty")
            elif len(data.name.strip()) > 255:
                errors.append("Tournament name must be 255 characters or less")
        
        # Validate location (if provided)
        if data.location is not None:
            if not data.location.strip():
                errors.append("Tournament location cannot be empty")
            elif len(data.location.strip()) > 255:
                errors.append("Tournament location must be 255 characters or less")
        
        # Validate description (if provided)
        if data.description is not None and len(data.description) > 1000:
            errors.append("Tournament description must be 1000 characters or less")
        
        # Validate dates (if provided)
        if data.start_date and data.end_date:
            if data.start_date >= data.end_date:
                errors.append("Start date must be before end date")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_tournament_status_transition(self, current_status: str, new_status: str) -> ValidationResult:
        """Validate tournament status transitions."""
        errors = []
        
        valid_transitions = {
            "setup": ["active", "cancelled"],
            "active": ["running", "paused", "cancelled"],
            "running": ["paused", "completed", "cancelled"],
            "paused": ["running", "cancelled"],
            "completed": [],  # Cannot change from completed
            "cancelled": []   # Cannot change from cancelled
        }
        
        if current_status not in valid_transitions:
            errors.append(f"Invalid current status: {current_status}")
        elif new_status not in valid_transitions.get(current_status, []):
            errors.append(f"Cannot transition from {current_status} to {new_status}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
