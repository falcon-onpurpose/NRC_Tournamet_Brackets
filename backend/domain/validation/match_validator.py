"""
Match validation logic for the validation domain.
"""
from typing import List, Dict, Any

from domain.validation.validation_result import ValidationResult
from schemas import SwissMatchCreate, EliminationMatchCreate


class MatchValidator:
    """Validator for match-related operations in validation domain."""
    
    def __init__(self):
        self.valid_match_statuses = [
            "scheduled",
            "in_progress",
            "completed",
            "cancelled",
            "forfeited"
        ]
    
    def validate_match_data(self, data: SwissMatchCreate) -> ValidationResult:
        """
        Validate Swiss match creation data.
        
        Args:
            data: Swiss match creation data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate tournament ID
        if data.tournament_id <= 0:
            errors.append("Valid tournament ID is required")
        
        # Validate teams
        if data.team1_id <= 0:
            errors.append("Valid team 1 ID is required")
        if data.team2_id <= 0:
            errors.append("Valid team 2 ID is required")
        if data.team1_id == data.team2_id:
            errors.append("Team 1 and Team 2 must be different")
        
        # Validate round number
        if hasattr(data, 'round_number') and data.round_number <= 0:
            errors.append("Round number must be positive")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_elimination_match_data(self, data: EliminationMatchCreate) -> ValidationResult:
        """
        Validate elimination match creation data.
        
        Args:
            data: Elimination match creation data
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate tournament ID
        if data.tournament_id <= 0:
            errors.append("Valid tournament ID is required")
        
        # Validate bracket ID
        if data.bracket_id <= 0:
            errors.append("Valid bracket ID is required")
        
        # Validate teams
        if data.team1_id <= 0:
            errors.append("Valid team 1 ID is required")
        if data.team2_id <= 0:
            errors.append("Valid team 2 ID is required")
        if data.team1_id == data.team2_id:
            errors.append("Team 1 and Team 2 must be different")
        
        # Validate round number
        if hasattr(data, 'round_number') and data.round_number <= 0:
            errors.append("Round number must be positive")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_match_result(self, winner_id: int, scores: Dict[str, Any]) -> ValidationResult:
        """
        Validate match result data.
        
        Args:
            winner_id: ID of the winning team
            scores: Match scores
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate winner ID
        if winner_id <= 0:
            errors.append("Valid winner ID is required")
        
        # Validate scores
        if not scores:
            errors.append("Match scores are required")
        elif not isinstance(scores, dict):
            errors.append("Scores must be a dictionary")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_match_status(self, status: str) -> ValidationResult:
        """Validate match status."""
        errors = []
        
        if status not in self.valid_match_statuses:
            errors.append(f"Invalid match status. Must be one of: {', '.join(self.valid_match_statuses)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
