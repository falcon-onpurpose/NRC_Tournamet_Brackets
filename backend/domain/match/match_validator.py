"""
Match validation logic.
"""
from typing import List, Optional
from dataclasses import dataclass

from schemas import MatchResultCreate


@dataclass
class ValidationResult:
    """Validation result with success status and error messages."""
    is_valid: bool
    errors: List[str]


class MatchValidator:
    """Validator for match-related operations."""
    
    def validate_match_result(self, result_data: MatchResultCreate) -> ValidationResult:
        """Validate match result data."""
        errors = []
        
        # Winner validation
        if not result_data.winner_id:
            errors.append("Winner ID is required")
        elif result_data.winner_id <= 0:
            errors.append("Winner ID must be positive")
        
        # Score validation
        if result_data.team1_score is None:
            errors.append("Team 1 score is required")
        elif result_data.team1_score < 0:
            errors.append("Team 1 score cannot be negative")
        
        if result_data.team2_score is None:
            errors.append("Team 2 score is required")
        elif result_data.team2_score < 0:
            errors.append("Team 2 score cannot be negative")
        
        # Winner must be one of the teams
        if result_data.winner_id and result_data.team1_id and result_data.team2_id:
            if result_data.winner_id not in [result_data.team1_id, result_data.team2_id]:
                errors.append("Winner must be one of the participating teams")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_swiss_match_data(self, tournament_id: int, team1_id: int, team2_id: int, round_number: int) -> ValidationResult:
        """Validate Swiss match creation data."""
        errors = []
        
        # Tournament validation
        if not tournament_id or tournament_id <= 0:
            errors.append("Valid tournament ID is required")
        
        # Team validation
        if not team1_id or team1_id <= 0:
            errors.append("Valid team 1 ID is required")
        
        if not team2_id or team2_id <= 0:
            errors.append("Valid team 2 ID is required")
        
        if team1_id == team2_id:
            errors.append("Team 1 and Team 2 cannot be the same")
        
        # Round validation
        if not round_number or round_number <= 0:
            errors.append("Valid round number is required")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_elimination_match_data(self, tournament_id: int, team1_id: int, team2_id: int, 
                                      bracket_id: int, round_number: int) -> ValidationResult:
        """Validate elimination match creation data."""
        errors = []
        
        # Tournament validation
        if not tournament_id or tournament_id <= 0:
            errors.append("Valid tournament ID is required")
        
        # Team validation
        if not team1_id or team1_id <= 0:
            errors.append("Valid team 1 ID is required")
        
        if not team2_id or team2_id <= 0:
            errors.append("Valid team 2 ID is required")
        
        if team1_id == team2_id:
            errors.append("Team 1 and Team 2 cannot be the same")
        
        # Bracket validation
        if not bracket_id or bracket_id <= 0:
            errors.append("Valid bracket ID is required")
        
        # Round validation
        if not round_number or round_number <= 0:
            errors.append("Valid round number is required")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_match_exists(self, match_id: int) -> ValidationResult:
        """Validate that match exists."""
        if match_id <= 0:
            return ValidationResult(
                is_valid=False,
                errors=["Invalid match ID"]
            )
        return ValidationResult(is_valid=True, errors=[])
    
    def validate_match_status(self, current_status: str, new_status: str) -> ValidationResult:
        """Validate match status transitions."""
        errors = []
        
        valid_transitions = {
            "pending": ["in_progress", "cancelled"],
            "in_progress": ["completed", "cancelled"],
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
    
    def validate_team_participation(self, team1_id: int, team2_id: int, tournament_id: int) -> ValidationResult:
        """Validate that teams can participate in the match."""
        errors = []
        
        # This would typically check against the database
        # For now, we'll do basic validation
        if team1_id == team2_id:
            errors.append("Teams cannot play against themselves")
        
        if not team1_id or not team2_id:
            errors.append("Both teams must be specified")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
