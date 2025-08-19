"""
Import orchestrator that coordinates all CSV import components.
"""
from typing import List, Dict, Any, Optional

from domain.csv_import.import_result import ImportResult, ImportError, ImportSeverity
from domain.csv_import.csv_parser import CSVParser
from domain.csv_import.data_sanitizer import DataSanitizer
from domain.csv_import.data_extractor import DataExtractor
from domain.validation.validation_service import ValidationService


class ImportOrchestrator:
    """Orchestrates the CSV import process using all domain components."""
    
    def __init__(self, validation_service: ValidationService):
        self.validation_service = validation_service
        self.csv_parser = CSVParser()
        self.data_sanitizer = DataSanitizer()
        self.data_extractor = DataExtractor(validation_service, self.data_sanitizer)
    
    def import_tournament_data(
        self,
        csv_data: str,
        tournament_id: int,
        strict_mode: bool = False
    ) -> ImportResult:
        """
        Import tournament data from CSV with comprehensive validation.
        
        Args:
            csv_data: Raw CSV data string
            tournament_id: Tournament ID to associate data with
            strict_mode: If True, fail on any validation error
            
        Returns:
            ImportResult with detailed results and errors
        """
        # Initialize result
        result = ImportResult.create_empty()
        
        # Step 1: Validate CSV structure
        if not self.csv_parser.validate_csv_structure(csv_data, result):
            return result
        
        # Step 2: Parse CSV data
        parsed_rows = self.csv_parser.parse_csv_data(csv_data, result)
        if not parsed_rows:
            return result
        
        # Step 3: Process each row
        self._process_rows(parsed_rows, tournament_id, strict_mode, result)
        
        # Step 4: Final validation
        result.success = result.success and (len(result.errors) == 0 or not strict_mode)
        
        return result
    
    def _process_rows(
        self,
        csv_rows: List[Dict[str, Any]],
        tournament_id: int,
        strict_mode: bool,
        result: ImportResult
    ) -> None:
        """Process all CSV rows and extract entities."""
        # Track processed entities to avoid duplicates
        processed_teams = {}  # team_name -> team_data
        processed_robots = {}  # (team_name, robot_name) -> robot_data
        processed_players = {}  # (team_name, first_name, last_name) -> player_data
        
        for row_index, row_data in enumerate(csv_rows, start=1):
            try:
                # Step 1: Sanitize row data
                sanitized_row = self.data_sanitizer.sanitize_row_data(row_data, row_index, result)
                
                if not sanitized_row:
                    continue  # Skip row if critical sanitization failed
                
                # Step 2: Extract and validate team data
                team_data = self.data_extractor.extract_team_data(
                    sanitized_row, tournament_id, row_index, result
                )
                if team_data:
                    team_key = team_data["name"].lower()
                    if team_key not in processed_teams:
                        processed_teams[team_key] = team_data
                        result.add_team_created(team_data)
                
                # Step 3: Extract and validate robot data
                robot_data = self.data_extractor.extract_robot_data(sanitized_row, row_index, result)
                if robot_data and team_data:
                    robot_key = (team_data["name"].lower(), robot_data["name"].lower())
                    if robot_key not in processed_robots:
                        processed_robots[robot_key] = robot_data
                        result.add_robot_created(robot_data)
                
                # Step 4: Extract and validate player data
                player_data = self.data_extractor.extract_player_data(sanitized_row, row_index, result)
                if player_data and team_data:
                    player_key = (
                        team_data["name"].lower(),
                        player_data["first_name"].lower(),
                        player_data["last_name"].lower()
                    )
                    if player_key not in processed_players:
                        processed_players[player_key] = player_data
                        result.add_player_created(player_data)
                
                result.processed_rows += 1
                
            except Exception as e:
                self._add_error(result, row_index, "general", ImportSeverity.CRITICAL,
                              f"Unexpected error processing row: {str(e)}", row_data)
                if strict_mode:
                    result.success = False
                    break
    
    def generate_import_report(self, result: ImportResult) -> str:
        """Generate a human-readable import report."""
        report_lines = []
        
        # Summary
        report_lines.append("=== CSV Import Report ===")
        report_lines.append(f"Success: {'Yes' if result.success else 'No'}")
        report_lines.append(f"Total Rows: {result.total_rows}")
        report_lines.append(f"Processed Rows: {result.processed_rows}")
        report_lines.append(f"Successful Imports: {result.successful_imports}")
        report_lines.append("")
        
        # Created entities
        report_lines.append("=== Created Entities ===")
        report_lines.append(f"Teams Created: {len(result.teams_created)}")
        report_lines.append(f"Robots Created: {len(result.robots_created)}")
        report_lines.append(f"Players Created: {len(result.players_created)}")
        report_lines.append("")
        
        # Errors
        if result.errors:
            report_lines.append("=== Errors ===")
            for error in result.errors:
                report_lines.append(f"Row {error.row}, {error.column}: {error.message}")
            report_lines.append("")
        
        # Warnings
        if result.warnings:
            report_lines.append("=== Warnings ===")
            for warning in result.warnings:
                report_lines.append(f"Row {warning.row}, {warning.column}: {warning.message}")
            report_lines.append("")
        
        return "\n".join(report_lines)
    
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
