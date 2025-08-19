"""
Data sanitization logic for CSV import operations.
"""
import re
import html
from typing import Dict, Any, Optional

from domain.csv_import.import_result import ImportResult, ImportError, ImportSeverity


class DataSanitizer:
    """Handles data sanitization and cleaning for CSV import."""
    
    def __init__(self):
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
    
    def sanitize_row_data(
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
    
    def clip_string(
        self,
        value: str,
        field_type: str,
        row_index: int,
        result: ImportResult
    ) -> str:
        """Clip string to maximum length and add warning if needed."""
        if not value:
            return value
        
        max_length = self.field_limits.get(field_type, 255)
        
        if len(value) > max_length:
            clipped_value = value[:max_length]
            self._add_error(result, row_index, field_type, ImportSeverity.WARNING,
                          f"Value truncated from {len(value)} to {max_length} characters",
                          value, clipped_value)
            return clipped_value
        
        return value
    
    def sanitize_phone(
        self,
        phone: str,
        row_index: int,
        result: ImportResult
    ) -> Optional[str]:
        """Sanitize and validate phone number."""
        if not phone:
            return None
        
        # Remove all non-digit characters
        digits_only = re.sub(r'[^\d]', '', phone)
        
        # Validate phone number format
        if len(digits_only) < 10:
            self._add_error(result, row_index, "phone", ImportSeverity.WARNING,
                          f"Phone number too short: {phone}", phone)
            return None
        elif len(digits_only) > 15:
            self._add_error(result, row_index, "phone", ImportSeverity.WARNING,
                          f"Phone number too long: {phone}", phone)
            return None
        
        # Format as (XXX) XXX-XXXX
        if len(digits_only) == 10:
            formatted = f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        else:
            formatted = digits_only
        
        return self.clip_string(formatted, "phone", row_index, result)
    
    def validate_email(
        self,
        email: str,
        row_index: int,
        result: ImportResult
    ) -> Optional[str]:
        """Validate and sanitize email address."""
        if not email:
            return None
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            self._add_error(result, row_index, "email", ImportSeverity.WARNING,
                          f"Invalid email format: {email}", email)
            return None
        
        return self.clip_string(email, "email", row_index, result)
    
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
