"""
Shared validation result class.
"""
from typing import List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    errors: List[str]
    
    @classmethod
    def success(cls) -> 'ValidationResult':
        """Create a successful validation result."""
        return cls(is_valid=True, errors=[])
    
    @classmethod
    def failure(cls, errors: List[str]) -> 'ValidationResult':
        """Create a failed validation result."""
        return cls(is_valid=False, errors=errors)
    
    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.is_valid = False
