"""
Import result classes for CSV import operations.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


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
    
    @classmethod
    def create_empty(cls) -> 'ImportResult':
        """Create an empty import result."""
        return cls(
            success=False,
            total_rows=0,
            processed_rows=0,
            successful_imports=0,
            errors=[],
            warnings=[],
            teams_created=[],
            robots_created=[],
            players_created=[]
        )
    
    def add_error(self, error: ImportError) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        if error.severity in [ImportSeverity.ERROR, ImportSeverity.CRITICAL]:
            self.success = False
    
    def add_warning(self, warning: ImportError) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def add_team_created(self, team: Dict[str, Any]) -> None:
        """Add a created team to the result."""
        self.teams_created.append(team)
        self.successful_imports += 1
    
    def add_robot_created(self, robot: Dict[str, Any]) -> None:
        """Add a created robot to the result."""
        self.robots_created.append(robot)
        self.successful_imports += 1
    
    def add_player_created(self, player: Dict[str, Any]) -> None:
        """Add a created player to the result."""
        self.players_created.append(player)
        self.successful_imports += 1
