"""
Validation service for data validation across the application.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from schemas import (
    TournamentCreate, TournamentUpdate, SwissMatchCreate, EliminationMatchCreate,
    TeamCreate, TeamUpdate, RobotCreate, RobotUpdate, PlayerCreate, PlayerUpdate
)


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    errors: List[str]


class ValidationService:
    """
    Service for validating data across the application.
    Provides centralized validation logic.
    """
    
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
        
        self.valid_match_statuses = [
            "scheduled",
            "in_progress",
            "completed",
            "cancelled",
            "forfeited"
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
        if data.format not in self.valid_tournament_formats:
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
        if data.format in ["swiss", "hybrid_swiss_elimination"]:
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
        
        # Validate name if provided
        if data.name is not None:
            if not data.name.strip():
                errors.append("Tournament name cannot be empty")
            elif len(data.name.strip()) > 255:
                errors.append("Tournament name must be 255 characters or less")
        
        # Validate format if provided
        if data.format is not None and data.format not in self.valid_tournament_formats:
            errors.append(f"Invalid tournament format. Must be one of: {', '.join(self.valid_tournament_formats)}")
        
        # Validate location if provided
        if data.location is not None:
            if not data.location.strip():
                errors.append("Tournament location cannot be empty")
            elif len(data.location.strip()) > 255:
                errors.append("Tournament location must be 255 characters or less")
        
        # Validate description if provided
        if data.description is not None and len(data.description) > 1000:
            errors.append("Tournament description must be 1000 characters or less")
        
        # Validate Swiss rounds if provided
        if data.swiss_rounds_count is not None:
            if data.swiss_rounds_count < 1:
                errors.append("Swiss rounds must be at least 1")
            elif data.swiss_rounds_count > 20:
                errors.append("Swiss rounds cannot exceed 20")
        
        # Validate dates if provided
        if data.start_date is not None and data.end_date is not None:
            if data.start_date >= data.end_date:
                errors.append("Start date must be before end date")
        
        if data.start_date is not None and data.start_date < datetime.utcnow():
            errors.append("Start date cannot be in the past")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
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
        if hasattr(data, 'tournament_id') and data.tournament_id is not None and data.tournament_id <= 0:
            errors.append("Invalid tournament ID")
        
        # Validate team IDs
        if data.team1_id <= 0:
            errors.append("Invalid team1 ID")
        
        if data.team2_id <= 0:
            errors.append("Invalid team2 ID")
        
        # Validate teams are different
        if data.team1_id == data.team2_id:
            errors.append("Team1 and Team2 must be different teams")
        
        # Validate round number
        if hasattr(data, 'round_number') and data.round_number is not None:
            if data.round_number < 1:
                errors.append("Round number must be at least 1")
            elif data.round_number > 20:
                errors.append("Round number cannot exceed 20")
        
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
        
        # Validate bracket ID
        if data.bracket_id <= 0:
            errors.append("Invalid bracket ID")
        
        # Validate team IDs
        if data.team1_id <= 0:
            errors.append("Invalid team1 ID")
        
        if data.team2_id <= 0:
            errors.append("Invalid team2 ID")
        
        # Validate teams are different
        if data.team1_id == data.team2_id:
            errors.append("Team1 and Team2 must be different teams")
        
        # Validate round number
        if data.round_number < 1:
            errors.append("Round number must be at least 1")
        elif data.round_number > 10:
            errors.append("Round number cannot exceed 10")
        
        # Validate match number
        if data.match_number < 1:
            errors.append("Match number must be at least 1")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
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
        
        # Validate email
        if data.email:
            if len(data.email) > 255:
                errors.append("Email must be 255 characters or less")
            elif '@' not in data.email:
                errors.append("Email must be a valid email address")
        
        # Validate phone
        if data.phone and len(data.phone) > 50:
            errors.append("Phone must be 50 characters or less")
        
        # Validate address
        if data.address and len(data.address) > 500:
            errors.append("Address must be 500 characters or less")
        
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
        
        # Validate name if provided
        if data.name is not None:
            if not data.name.strip():
                errors.append("Team name cannot be empty")
            elif len(data.name.strip()) > 100:
                errors.append("Team name must be 100 characters or less")
        
        # Validate email if provided
        if data.email is not None:
            if len(data.email) > 255:
                errors.append("Email must be 255 characters or less")
            elif '@' not in data.email:
                errors.append("Email must be a valid email address")
        
        # Validate phone if provided
        if data.phone is not None and len(data.phone) > 50:
            errors.append("Phone must be 50 characters or less")
        
        # Validate address if provided
        if data.address is not None and len(data.address) > 500:
            errors.append("Address must be 500 characters or less")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    # Robot Validation Methods
    
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
        
        # Validate name if provided
        if data.name is not None:
            if not data.name.strip():
                errors.append("Robot name cannot be empty")
            elif len(data.name.strip()) > 100:
                errors.append("Robot name must be 100 characters or less")
        
        # Validate comments if provided
        if data.comments is not None and len(data.comments) > 1000:
            errors.append("Robot comments must be 1000 characters or less")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    # Player Validation Methods
    
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
        
        # Validate first name if provided
        if data.first_name is not None:
            if not data.first_name.strip():
                errors.append("Player first name cannot be empty")
            elif len(data.first_name.strip()) > 50:
                errors.append("Player first name must be 50 characters or less")
        
        # Validate last name if provided
        if data.last_name is not None:
            if not data.last_name.strip():
                errors.append("Player last name cannot be empty")
            elif len(data.last_name.strip()) > 50:
                errors.append("Player last name must be 50 characters or less")
        
        # Validate email if provided
        if data.email is not None:
            if len(data.email) > 255:
                errors.append("Player email must be 255 characters or less")
            elif '@' not in data.email:
                errors.append("Player email must be a valid email address")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_csv_import_data(self, csv_data: str) -> ValidationResult:
        """
        Validate CSV import data format.
        
        Args:
            csv_data: CSV data string
            
        Returns:
            Validation result
        """
        errors = []
        
        if not csv_data or not csv_data.strip():
            errors.append("CSV data is required")
            return ValidationResult(is_valid=False, errors=errors)
        
        lines = csv_data.strip().split('\n')
        if len(lines) < 2:
            errors.append("CSV must have at least a header row and one data row")
            return ValidationResult(is_valid=False, errors=errors)
        
        # Check required headers
        header_line = lines[0]
        required_headers = ["Team", "Robot_Name", "Robot_Weightclass"]
        missing_headers = []
        
        for header in required_headers:
            if header not in header_line:
                missing_headers.append(header)
        
        if missing_headers:
            errors.append(f"Missing required headers: {', '.join(missing_headers)}")
        
        # Check data rows
        for i, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue  # Skip empty lines
            
            fields = line.split(',')
            if len(fields) < len(required_headers):
                errors.append(f"Row {i}: Insufficient data fields")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_match_result(self, winner_id: int, scores: Dict[str, Any]) -> ValidationResult:
        """
        Validate match result data.
        
        Args:
            winner_id: ID of winning team
            scores: Match scores dictionary
            
        Returns:
            Validation result
        """
        errors = []
        
        # Validate winner ID
        if winner_id <= 0:
            errors.append("Invalid winner ID")
        
        # Validate scores
        if not scores:
            errors.append("Match scores are required")
        else:
            # Check for required score fields
            required_score_fields = ["team1_score", "team2_score"]
            for field in required_score_fields:
                if field not in scores:
                    errors.append(f"Missing required score field: {field}")
                else:
                    try:
                        score = int(scores[field])
                        if score < 0:
                            errors.append(f"{field} cannot be negative")
                    except (ValueError, TypeError):
                        errors.append(f"{field} must be a valid integer")
            
            # Validate winner matches scores
            if "team1_score" in scores and "team2_score" in scores:
                try:
                    team1_score = int(scores["team1_score"])
                    team2_score = int(scores["team2_score"])
                    
                    if team1_score == team2_score:
                        errors.append("Match cannot end in a tie")
                    else:
                        # Check if winner ID matches the higher score only when not a tie
                        if winner_id == 1 and team1_score <= team2_score:
                            errors.append("Winner ID does not match scores")
                        elif winner_id == 2 and team2_score <= team1_score:
                            errors.append("Winner ID does not match scores")
                        
                except (ValueError, TypeError):
                    errors.append("Invalid score values")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
