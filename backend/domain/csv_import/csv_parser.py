"""
CSV parsing logic for CSV import operations.
"""
import csv
import io
from typing import List, Dict, Any, Optional

from domain.csv_import.import_result import ImportResult, ImportError, ImportSeverity


class CSVParser:
    """Handles CSV parsing and validation."""
    
    def __init__(self):
        self.required_headers = ["Team", "Robot_Name", "Robot_Weightclass"]
        self.optional_headers = [
            "First_Name", "Last_Name", "Email", "Team_Address", 
            "Team_Phone", "Comments", "Waitlist", "Robot_Fee_Paid"
        ]
    
    def parse_csv_data(
        self,
        csv_data: str,
        result: ImportResult
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Parse CSV data and validate structure.
        
        Args:
            csv_data: Raw CSV data string
            result: Import result to track errors
            
        Returns:
            List of row dictionaries or None if parsing failed
        """
        if not csv_data or not csv_data.strip():
            self._add_error(result, 0, "CSV", ImportSeverity.ERROR,
                          "CSV data is required", "")
            return None
        
        try:
            # Parse CSV data
            csv_file = io.StringIO(csv_data.strip())
            reader = csv.DictReader(csv_file)
            
            # Validate headers
            if not reader.fieldnames:
                self._add_error(result, 0, "CSV", ImportSeverity.ERROR,
                              "CSV must have headers", "")
                return None
            
            # Check required headers
            missing_headers = []
            for header in self.required_headers:
                if header not in reader.fieldnames:
                    missing_headers.append(header)
            
            if missing_headers:
                self._add_error(result, 0, "CSV", ImportSeverity.ERROR,
                              f"Missing required headers: {', '.join(missing_headers)}", 
                              list(reader.fieldnames))
                return None
            
            # Parse rows
            rows = []
            for row_index, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                if not any(row.values()):  # Skip empty rows
                    continue
                
                # Validate row has minimum required data
                if not self._validate_row_data(row, row_index, result):
                    continue
                
                rows.append(row)
            
            result.total_rows = len(rows)
            result.processed_rows = len(rows)
            
            return rows
            
        except Exception as e:
            self._add_error(result, 0, "CSV", ImportSeverity.CRITICAL,
                          f"Failed to parse CSV: {str(e)}", "")
            return None
    
    def validate_csv_structure(
        self,
        csv_data: str,
        result: ImportResult
    ) -> bool:
        """
        Validate CSV structure without parsing all data.
        
        Args:
            csv_data: Raw CSV data string
            result: Import result to track errors
            
        Returns:
            True if structure is valid, False otherwise
        """
        if not csv_data or not csv_data.strip():
            self._add_error(result, 0, "CSV", ImportSeverity.ERROR,
                          "CSV data is required", "")
            return False
        
        try:
            # Check if we have at least 2 lines (header + data)
            lines = csv_data.strip().split('\n')
            if len(lines) < 2:
                self._add_error(result, 0, "CSV", ImportSeverity.ERROR,
                              "CSV must have at least a header row and one data row", "")
                return False
            
            # Parse header
            csv_file = io.StringIO(csv_data.strip())
            reader = csv.DictReader(csv_file)
            
            if not reader.fieldnames:
                self._add_error(result, 0, "CSV", ImportSeverity.ERROR,
                              "CSV must have valid headers", "")
                return False
            
            # Check required headers
            missing_headers = []
            for header in self.required_headers:
                if header not in reader.fieldnames:
                    missing_headers.append(header)
            
            if missing_headers:
                self._add_error(result, 0, "CSV", ImportSeverity.ERROR,
                              f"Missing required headers: {', '.join(missing_headers)}", 
                              list(reader.fieldnames))
                return False
            
            return True
            
        except Exception as e:
            self._add_error(result, 0, "CSV", ImportSeverity.CRITICAL,
                          f"Failed to validate CSV structure: {str(e)}", "")
            return False
    
    def _validate_row_data(
        self,
        row: Dict[str, Any],
        row_index: int,
        result: ImportResult
    ) -> bool:
        """Validate that row has minimum required data."""
        # Check if we have at least one required field with data
        has_required_data = False
        
        for header in self.required_headers:
            if header in row and row[header] and str(row[header]).strip():
                has_required_data = True
                break
        
        if not has_required_data:
            self._add_error(result, row_index, "CSV", ImportSeverity.WARNING,
                          "Row has no required data, skipping", row)
            return False
        
        return True
    
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
