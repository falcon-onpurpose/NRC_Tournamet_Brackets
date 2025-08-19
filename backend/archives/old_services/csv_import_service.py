"""
CSV Import Service - Handles robust CSV data import with comprehensive validation.

This service provides:
- Data sanitization and validation
- String length enforcement
- Type conversion and validation
- Business logic validation
- Error handling and reporting
- Partial import support
"""

import re
import html
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from schemas import TeamCreate, RobotCreate, PlayerCreate
from services.validation_service import ValidationService


class ImportSeverity(Enum):
    """Import error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ImportError:
    """Import error details."""
    row: int
    column: str
    severity: ImportSeverity
    message: str
    original_value: Any
    corrected_value: Any = None


@dataclass
class ImportResult:
    """Import operation result."""
    success: bool
    total_rows: int
    processed_rows: int
    successful_imports: int
    errors: List[ImportError]
    warnings: List[ImportError]
    teams_created: List[Dict[str, Any]]
    robots_created: List[Dict[str, Any]]
    players_created: List[Dict[str, Any]]


class CSVImportService:
    """Service for robust CSV data import with comprehensive validation."""
    
    def __init__(self, settings):
        self.settings = settings
        self.validation_service = ValidationService()
        
        # Field length limits (from schemas)
        self.field_limits = {
            "team_name": 100,
            "robot_name": 100,
            "first_name": 50,
            "last_name": 50,
            "email": 255,
            "phone": 50,
            "address": 500,
            "comments": 1000
        }
        
        # Robot class mappings
        self.robot_class_mappings = {
            "150g - Non-Destructive": "antweight_non_destructive",
            "150g - Antweight Destructive": "antweight_destructive", 
            "150g - Destructive": "antweight_destructive",
            "Beetleweight": "beetleweight",
            "Antweight": "antweight_destructive"  # Default antweight
        }
    
    def import_tournament_data(
        self,
        csv_data: List[Dict[str, Any]],
        tournament_id: int,
        strict_mode: bool = False
    ) -> ImportResult:
        """
        Import tournament data from CSV with comprehensive validation.
        
        Args:
            csv_data: List of CSV row dictionaries
            tournament_id: Tournament ID to associate data with
            strict_mode: If True, fail on any validation error
            
        Returns:
            ImportResult with detailed results and errors
        """
        result = ImportResult(
            success=True,
            total_rows=len(csv_data),
            processed_rows=0,
            successful_imports=0,
            errors=[],
            warnings=[],
            teams_created=[],
            robots_created=[],
            players_created=[]
        )
        
        # Track processed entities to avoid duplicates
        processed_teams = {}  # team_name -> team_data
        processed_robots = {}  # (team_name, robot_name) -> robot_data
        processed_players = {}  # (team_name, first_name, last_name) -> player_data
        
        for row_index, row_data in enumerate(csv_data, start=1):
            try:
                # Sanitize and validate row data
                sanitized_row = self._sanitize_row_data(row_data, row_index, result)
                
                if not sanitized_row:
                    continue  # Skip row if critical sanitization failed
                
                # Extract and validate team data
                team_data = self._extract_team_data(sanitized_row, tournament_id, row_index, result)
                if team_data:
                    team_key = team_data["name"].lower()
                    if team_key not in processed_teams:
                        processed_teams[team_key] = team_data
                        result.teams_created.append(team_data)
                
                # Extract and validate robot data
                robot_data = self._extract_robot_data(sanitized_row, row_index, result)
                if robot_data and team_data:
                    robot_key = (team_data["name"].lower(), robot_data["name"].lower())
                    if robot_key not in processed_robots:
                        processed_robots[robot_key] = robot_data
                        result.robots_created.append(robot_data)
                
                # Extract and validate player data
                player_data = self._extract_player_data(sanitized_row, row_index, result)
                if player_data and team_data:
                    player_key = (
                        team_data["name"].lower(),
                        player_data["first_name"].lower(),
                        player_data["last_name"].lower()
                    )
                    if player_key not in processed_players:
                        processed_players[player_key] = player_data
                        result.players_created.append(player_data)
                
                result.processed_rows += 1
                result.successful_imports += 1
                
            except Exception as e:
                self._add_error(result, row_index, "general", ImportSeverity.CRITICAL,
                              f"Unexpected error processing row: {str(e)}", row_data)
                if strict_mode:
                    result.success = False
                    break
        
        # Final validation
        result.success = result.success and (len(result.errors) == 0 or not strict_mode)
        
        return result
    
    def _sanitize_row_data(
        self,
        row_data: Dict[str, Any],
        row_index: int,
        result: ImportResult
    ) -> Optional[Dict[str, Any]]:
        """Sanitize and validate row data."""
        sanitized = {}
        
        for key, value in row_data.items():
            try:
                # Convert to string and handle None/empty values
                if value is None:
                    sanitized_value = ""
                else:
                    sanitized_value = str(value).strip()
                
                # HTML escape to prevent injection
                sanitized_value = html.escape(sanitized_value)
                
                # Remove/replace potentially dangerous characters
                sanitized_value = re.sub(r'[<>"\'\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized_value)
                
                # Normalize whitespace
                sanitized_value = re.sub(r'\s+', ' ', sanitized_value).strip()
                
                sanitized[key] = sanitized_value
                
            except Exception as e:
                self._add_error(result, row_index, key, ImportSeverity.WARNING,
                              f"Failed to sanitize field: {str(e)}", value)
                sanitized[key] = ""
        
        return sanitized
    
    def _extract_team_data(
        self,
        row_data: Dict[str, Any],
        tournament_id: int,
        row_index: int,
        result: ImportResult
    ) -> Optional[Dict[str, Any]]:
        """Extract and validate team data from row."""
        team_name = row_data.get("Team", "").strip()
        
        if not team_name:
            self._add_error(result, row_index, "Team", ImportSeverity.ERROR,
                          "Team name is required", "")
            return None
        
        # Clip team name to max length
        original_name = team_name
        team_name = self._clip_string(team_name, "team_name", row_index, result)
        
        # Extract and validate other team fields
        address = self._clip_string(row_data.get("Team_Address", ""), "address", row_index, result)
        phone = self._sanitize_phone(row_data.get("Team_Phone", ""), row_index, result)
        email = self._validate_email(row_data.get("Email", ""), row_index, result)
        
        team_data = {
            "name": team_name,
            "address": address if address else None,
            "phone": phone if phone else None,
            "email": email if email else None
        }
        
        # Validate using TeamCreate schema
        try:
            team_create = TeamCreate(**team_data)
            validation_result = self.validation_service.validate_team_data(team_create)
            
            if not validation_result.is_valid:
                for error in validation_result.errors:
                    self._add_error(result, row_index, "Team", ImportSeverity.ERROR,
                                  f"Team validation failed: {error}", team_data)
                return None
                
        except Exception as e:
            self._add_error(result, row_index, "Team", ImportSeverity.ERROR,
                          f"Team schema validation failed: {str(e)}", team_data)
            return None
        
        return team_data
    
    def _extract_robot_data(
        self,
        row_data: Dict[str, Any],
        row_index: int,
        result: ImportResult
    ) -> Optional[Dict[str, Any]]:
        """Extract and validate robot data from row."""
        robot_name = row_data.get("Robot_Name", "").strip()
        
        if not robot_name:
            self._add_error(result, row_index, "Robot_Name", ImportSeverity.ERROR,
                          "Robot name is required", "")
            return None
        
        # Clip robot name to max length
        robot_name = self._clip_string(robot_name, "robot_name", row_index, result)
        
        # Map robot class
        robot_class_str = row_data.get("Robot_Weightclass", "").strip()
        robot_class_id = self._map_robot_class(robot_class_str, row_index, result)
        
        if not robot_class_id:
            return None
        
        # Parse boolean and numeric fields
        waitlist = self._parse_boolean(row_data.get("Waitlist", "false"), "Waitlist", row_index, result)
        fee_paid = self._parse_boolean(row_data.get("Robot_Fee_Paid", "false"), "Robot_Fee_Paid", row_index, result)
        
        # Extract comments
        comments = row_data.get("Comments", "").strip()
        if comments:
            comments = self._clip_string(comments, "comments", row_index, result)
        
        robot_data = {
            "name": robot_name,
            "robot_class_id": robot_class_id,
            "waitlist": waitlist,
            "fee_paid": fee_paid,
            "comments": comments if comments else None
        }
        
        # Validate using RobotCreate schema
        try:
            robot_create = RobotCreate(**robot_data)
            validation_result = self.validation_service.validate_robot_data(robot_create)
            
            if not validation_result.is_valid:
                for error in validation_result.errors:
                    self._add_error(result, row_index, "Robot", ImportSeverity.ERROR,
                                  f"Robot validation failed: {error}", robot_data)
                return None
                
        except Exception as e:
            self._add_error(result, row_index, "Robot", ImportSeverity.ERROR,
                          f"Robot schema validation failed: {str(e)}", robot_data)
            return None
        
        return robot_data
    
    def _extract_player_data(
        self,
        row_data: Dict[str, Any],
        row_index: int,
        result: ImportResult
    ) -> Optional[Dict[str, Any]]:
        """Extract and validate player data from row."""
        first_name = row_data.get("First_Name", "").strip()
        last_name = row_data.get("Last_Name", "").strip()
        
        if not first_name or not last_name:
            self._add_error(result, row_index, "Player", ImportSeverity.ERROR,
                          "Both first name and last name are required", 
                          {"first_name": first_name, "last_name": last_name})
            return None
        
        # Clip names to max length
        first_name = self._clip_string(first_name, "first_name", row_index, result)
        last_name = self._clip_string(last_name, "last_name", row_index, result)
        
        # Validate email
        email = self._validate_email(row_data.get("Email", ""), row_index, result)
        
        player_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email if email else None
        }
        
        # Validate using PlayerCreate schema
        try:
            player_create = PlayerCreate(**player_data)
            validation_result = self.validation_service.validate_player_data(player_create)
            
            if not validation_result.is_valid:
                for error in validation_result.errors:
                    self._add_error(result, row_index, "Player", ImportSeverity.ERROR,
                                  f"Player validation failed: {error}", player_data)
                return None
                
        except Exception as e:
            self._add_error(result, row_index, "Player", ImportSeverity.ERROR,
                          f"Player schema validation failed: {str(e)}", player_data)
            return None
        
        return player_data
    
    def _clip_string(
        self,
        value: str,
        field_type: str,
        row_index: int,
        result: ImportResult
    ) -> str:
        """Clip string to maximum allowed length."""
        if not value:
            return value
        
        max_length = self.field_limits.get(field_type, 255)
        
        if len(value) > max_length:
            clipped_value = value[:max_length]
            self._add_error(result, row_index, field_type, ImportSeverity.WARNING,
                          f"String clipped from {len(value)} to {max_length} characters",
                          value, clipped_value)
            return clipped_value
        
        return value
    
    def _sanitize_phone(
        self,
        phone: str,
        row_index: int,
        result: ImportResult
    ) -> str:
        """Sanitize phone number."""
        if not phone:
            return ""
        
        # Remove non-digit characters except + and spaces
        sanitized = re.sub(r'[^\d+\s()-]', '', phone)
        
        # Clip to max length
        sanitized = self._clip_string(sanitized, "phone", row_index, result)
        
        return sanitized
    
    def _validate_email(
        self,
        email: str,
        row_index: int,
        result: ImportResult
    ) -> str:
        """Validate email format."""
        if not email:
            return ""
        
        # Clip to max length first
        email = self._clip_string(email, "email", row_index, result)
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self._add_error(result, row_index, "email", ImportSeverity.WARNING,
                          "Invalid email format", email)
            return ""
        
        return email.lower()  # Normalize to lowercase
    
    def _map_robot_class(
        self,
        robot_class_str: str,
        row_index: int,
        result: ImportResult
    ) -> Optional[int]:
        """Map robot class string to database ID."""
        if not robot_class_str:
            self._add_error(result, row_index, "Robot_Weightclass", ImportSeverity.ERROR,
                          "Robot weightclass is required", "")
            return None
        
        # This would need to be updated to query actual robot class IDs from database
        # For now, return a placeholder ID based on the mapping
        class_mapping = {
            "antweight_non_destructive": 1,
            "antweight_destructive": 2,
            "beetleweight": 3
        }
        
        mapped_class = self.robot_class_mappings.get(robot_class_str)
        if not mapped_class:
            self._add_error(result, row_index, "Robot_Weightclass", ImportSeverity.ERROR,
                          f"Unknown robot class: {robot_class_str}", robot_class_str)
            return None
        
        return class_mapping.get(mapped_class, 1)  # Default to antweight non-destructive
    
    def _parse_boolean(
        self,
        value: str,
        field_name: str,
        row_index: int,
        result: ImportResult
    ) -> bool:
        """Parse boolean value from string."""
        if not value:
            return False
        
        value_lower = value.lower().strip()
        
        if value_lower in ["true", "1", "yes", "y", "on"]:
            return True
        elif value_lower in ["false", "0", "no", "n", "off", ""]:
            return False
        else:
            self._add_error(result, row_index, field_name, ImportSeverity.WARNING,
                          f"Invalid boolean value, defaulting to False", value)
            return False
    
    def _add_error(
        self,
        result: ImportResult,
        row: int,
        column: str,
        severity: ImportSeverity,
        message: str,
        original_value: Any,
        corrected_value: Any = None
    ):
        """Add an error to the import result."""
        error = ImportError(
            row=row,
            column=column,
            severity=severity,
            message=message,
            original_value=original_value,
            corrected_value=corrected_value
        )
        
        if severity in [ImportSeverity.ERROR, ImportSeverity.CRITICAL]:
            result.errors.append(error)
        else:
            result.warnings.append(error)
    
    def generate_import_report(self, result: ImportResult) -> str:
        """Generate a human-readable import report."""
        report = []
        report.append(f"CSV Import Report")
        report.append(f"================")
        report.append(f"Total rows processed: {result.total_rows}")
        report.append(f"Successful imports: {result.successful_imports}")
        report.append(f"Teams created: {len(result.teams_created)}")
        report.append(f"Robots created: {len(result.robots_created)}")
        report.append(f"Players created: {len(result.players_created)}")
        report.append(f"Errors: {len(result.errors)}")
        report.append(f"Warnings: {len(result.warnings)}")
        report.append("")
        
        if result.errors:
            report.append("ERRORS:")
            for error in result.errors:
                report.append(f"  Row {error.row}, {error.column}: {error.message}")
        
        if result.warnings:
            report.append("WARNINGS:")
            for warning in result.warnings:
                report.append(f"  Row {warning.row}, {warning.column}: {warning.message}")
        
        return "\n".join(report)
