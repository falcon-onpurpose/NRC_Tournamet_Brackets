"""
Centralized validation service that orchestrates all validators.
"""
from typing import Dict, Any

from domain.validation.validation_result import ValidationResult
from domain.validation.tournament_validator import TournamentValidator
from domain.validation.match_validator import MatchValidator
from domain.validation.team_validator import TeamValidator
from domain.validation.robot_validator import RobotValidator
from domain.validation.player_validator import PlayerValidator
from domain.validation.csv_validator import CSVValidator

from schemas import (
    TournamentCreate, TournamentUpdate, SwissMatchCreate, EliminationMatchCreate,
    TeamCreate, TeamUpdate, RobotCreate, RobotUpdate, PlayerCreate, PlayerUpdate
)


class ValidationService:
    """
    Centralized validation service that coordinates all domain validators.
    Provides a single entry point for all validation operations.
    """
    
    def __init__(self):
        self.tournament_validator = TournamentValidator()
        self.match_validator = MatchValidator()
        self.team_validator = TeamValidator()
        self.robot_validator = RobotValidator()
        self.player_validator = PlayerValidator()
        self.csv_validator = CSVValidator()
    
    # Tournament validation methods
    def validate_tournament_data(self, data: TournamentCreate) -> ValidationResult:
        """Validate tournament creation data."""
        return self.tournament_validator.validate_tournament_data(data)
    
    def validate_tournament_update(self, data: TournamentUpdate) -> ValidationResult:
        """Validate tournament update data."""
        return self.tournament_validator.validate_tournament_update(data)
    
    def validate_tournament_status_transition(self, current_status: str, new_status: str) -> ValidationResult:
        """Validate tournament status transitions."""
        return self.tournament_validator.validate_tournament_status_transition(current_status, new_status)
    
    # Match validation methods
    def validate_match_data(self, data: SwissMatchCreate) -> ValidationResult:
        """Validate Swiss match creation data."""
        return self.match_validator.validate_match_data(data)
    
    def validate_elimination_match_data(self, data: EliminationMatchCreate) -> ValidationResult:
        """Validate elimination match creation data."""
        return self.match_validator.validate_elimination_match_data(data)
    
    def validate_match_result(self, winner_id: int, scores: Dict[str, Any]) -> ValidationResult:
        """Validate match result data."""
        return self.match_validator.validate_match_result(winner_id, scores)
    
    def validate_match_status(self, status: str) -> ValidationResult:
        """Validate match status."""
        return self.match_validator.validate_match_status(status)
    
    # Team validation methods
    def validate_team_data(self, data: TeamCreate) -> ValidationResult:
        """Validate team creation data."""
        return self.team_validator.validate_team_data(data)
    
    def validate_team_update(self, data: TeamUpdate) -> ValidationResult:
        """Validate team update data."""
        return self.team_validator.validate_team_update(data)
    
    # Robot validation methods
    def validate_robot_data(self, data: RobotCreate) -> ValidationResult:
        """Validate robot creation data."""
        return self.robot_validator.validate_robot_data(data)
    
    def validate_robot_update(self, data: RobotUpdate) -> ValidationResult:
        """Validate robot update data."""
        return self.robot_validator.validate_robot_update(data)
    
    def validate_robot_exists(self, robot_id: int) -> ValidationResult:
        """Validate that robot exists."""
        return self.robot_validator.validate_robot_exists(robot_id)
    
    # Player validation methods
    def validate_player_data(self, data: PlayerCreate) -> ValidationResult:
        """Validate player creation data."""
        return self.player_validator.validate_player_data(data)
    
    def validate_player_update(self, data: PlayerUpdate) -> ValidationResult:
        """Validate player update data."""
        return self.player_validator.validate_player_update(data)
    
    def validate_player_exists(self, player_id: int) -> ValidationResult:
        """Validate that player exists."""
        return self.player_validator.validate_player_exists(player_id)
    
    # CSV validation methods
    def validate_csv_import_data(self, csv_data: str) -> ValidationResult:
        """Validate CSV import data format."""
        return self.csv_validator.validate_csv_import_data(csv_data)
    
    def validate_csv_file_format(self, filename: str) -> ValidationResult:
        """Validate CSV file format."""
        return self.csv_validator.validate_csv_file_format(filename)
    
    def validate_csv_file_size(self, file_size: int, max_size: int = 10 * 1024 * 1024) -> ValidationResult:
        """Validate CSV file size."""
        return self.csv_validator.validate_csv_file_size(file_size, max_size)
