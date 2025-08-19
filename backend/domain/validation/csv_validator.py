"""
CSV validation logic.
"""
from typing import List, Dict, Any

from domain.validation.validation_result import ValidationResult


class CSVValidator:
    """Validator for CSV import operations."""
    
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
    
    def validate_csv_file_format(self, filename: str) -> ValidationResult:
        """Validate CSV file format."""
        errors = []
        
        if not filename:
            errors.append("Filename is required")
        elif not filename.lower().endswith('.csv'):
            errors.append("File must be a CSV file")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_csv_file_size(self, file_size: int, max_size: int = 10 * 1024 * 1024) -> ValidationResult:
        """Validate CSV file size."""
        errors = []
        
        if file_size <= 0:
            errors.append("File size must be greater than 0")
        elif file_size > max_size:
            errors.append(f"File size exceeds maximum allowed size of {max_size} bytes")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
