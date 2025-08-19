"""
Data extraction logic for CSV import operations.
"""
from typing import Dict, Any, Optional

from schemas import TeamCreate, RobotCreate, PlayerCreate
from domain.validation.validation_service import ValidationService
from domain.csv_import.import_result import ImportResult, ImportError, ImportSeverity
from domain.csv_import.data_sanitizer import DataSanitizer


class DataExtractor:
    """Handles data extraction and validation for CSV import."""
    
    def __init__(self, validation_service: ValidationService, sanitizer: DataSanitizer):
        self.validation_service = validation_service
        self.sanitizer = sanitizer
        
        # Robot class mappings
        self.robot_class_mappings = {
            "150g - Non-Destructive": "antweight_non_destructive",
            "150g - Antweight Destructive": "antweight_destructive", 
            "150g - Destructive": "antweight_destructive",
            "Beetleweight": "beetleweight",
            "Antweight": "antweight_destructive"  # Default antweight
        }
    
    def extract_team_data(
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
        team_name = self.sanitizer.clip_string(team_name, "team_name", row_index, result)
        
        # Extract and validate other team fields
        address = self.sanitizer.clip_string(row_data.get("Team_Address", ""), "address", row_index, result)
        phone = self.sanitizer.sanitize_phone(row_data.get("Team_Phone", ""), row_index, result)
        email = self.sanitizer.validate_email(row_data.get("Email", ""), row_index, result)
        
        team_data = {
            "name": team_name,
            "tournament_id": tournament_id,
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
    
    def extract_robot_data(
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
        robot_name = self.sanitizer.clip_string(robot_name, "robot_name", row_index, result)
        
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
            comments = self.sanitizer.clip_string(comments, "comments", row_index, result)
        
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
    
    def extract_player_data(
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
        first_name = self.sanitizer.clip_string(first_name, "first_name", row_index, result)
        last_name = self.sanitizer.clip_string(last_name, "last_name", row_index, result)
        
        # Validate email
        email = self.sanitizer.validate_email(row_data.get("Email", ""), row_index, result)
        
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
    
    def _map_robot_class(
        self,
        robot_class_str: str,
        row_index: int,
        result: ImportResult
    ) -> Optional[int]:
        """Map robot class string to robot class ID."""
        if not robot_class_str:
            self._add_error(result, row_index, "Robot_Weightclass", ImportSeverity.ERROR,
                          "Robot weight class is required", "")
            return None
        
        # Map string to internal format
        mapped_class = self.robot_class_mappings.get(robot_class_str, robot_class_str)
        
        # TODO: This should query the database to get actual robot class IDs
        # For now, return a default value
        robot_class_id = 1  # Default to first robot class
        
        return robot_class_id
    
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
                          f"Invalid boolean value: {value}, defaulting to false", value)
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
    ) -> None:
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
            result.add_error(error)
        else:
            result.add_warning(error)
