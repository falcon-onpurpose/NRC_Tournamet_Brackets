"""
Simple unit tests for TeamService.
Tests initialization and validation integration without database interaction.
"""

import pytest
from services.team_service import TeamService
from services.validation_service import ValidationService
from schemas import TeamCreate, RobotCreate, PlayerCreate


class TestTeamServiceSimple:
    """Simple tests for TeamService functionality."""
    
    @pytest.fixture
    def team_service(self, test_settings):
        return TeamService(test_settings)
    
    def test_team_service_initialization(self, team_service):
        """Test TeamService initializes correctly."""
        assert team_service is not None
        assert team_service.settings is not None
        assert team_service.validation_service is not None
        assert isinstance(team_service.validation_service, ValidationService)
    
    def test_validation_service_integration(self, team_service):
        """Test TeamService integrates with ValidationService."""
        # Test team validation
        team_data = TeamCreate(
            name="Test Team",
            email="test@example.com"
        )
        validation_result = team_service.validation_service.validate_team_data(team_data)
        assert validation_result.is_valid is True
        
        # Test robot validation
        robot_data = RobotCreate(
            name="Test Robot",
            robot_class_id=1
        )
        validation_result = team_service.validation_service.validate_robot_data(robot_data)
        assert validation_result.is_valid is True
        
        # Test player validation
        player_data = PlayerCreate(
            first_name="Test",
            last_name="Player",
            email="player@example.com"
        )
        validation_result = team_service.validation_service.validate_player_data(player_data)
        assert validation_result.is_valid is True
    
    def test_team_validation_errors(self, team_service):
        """Test team validation error handling."""
        # Test invalid team data - this will fail at Pydantic level, so we test with valid data first
        valid_team_data = TeamCreate(
            name="Test Team",
            email="invalid-email"  # Invalid email format
        )
        validation_result = team_service.validation_service.validate_team_data(valid_team_data)
        assert validation_result.is_valid is False
        assert "Email must be a valid email address" in validation_result.errors
    
    def test_robot_validation_errors(self, team_service):
        """Test robot validation error handling."""
        # Test invalid robot data - this will fail at Pydantic level, so we test with valid data first
        valid_robot_data = RobotCreate(
            name="Test Robot",
            robot_class_id=0  # Invalid robot class ID
        )
        validation_result = team_service.validation_service.validate_robot_data(valid_robot_data)
        assert validation_result.is_valid is False
        assert "Valid robot class ID is required" in validation_result.errors
    
    def test_player_validation_errors(self, team_service):
        """Test player validation error handling."""
        # Test invalid player data - this will fail at Pydantic level, so we test with valid data first
        valid_player_data = PlayerCreate(
            first_name="Test",
            last_name="Player",
            email="invalid-email"  # Invalid email format
        )
        validation_result = team_service.validation_service.validate_player_data(valid_player_data)
        assert validation_result.is_valid is False
        assert "Player email must be a valid email address" in validation_result.errors
    
    def test_csv_row_parsing(self, team_service):
        """Test CSV row parsing functionality."""
        csv_row = {
            "Team": "Test Team",
            "Email": "test@example.com",
            "Team_Phone": "123-456-7890",
            "Team_Address": "123 Test St",
            "Comments": "Test notes"
        }
        
        team_data = team_service._parse_csv_row(csv_row, tournament_id=1)
        assert team_data.name == "Test Team"
        assert team_data.email == "test@example.com"
        assert team_data.phone == "123-456-7890"
        assert team_data.address == "123 Test St"
    
    def test_csv_row_parsing_missing_required(self, team_service):
        """Test CSV row parsing with missing required fields."""
        csv_row = {
            "Email": "test@example.com",
            # Missing "Team" field
        }
        
        with pytest.raises(ValueError, match="Team name is required"):
            team_service._parse_csv_row(csv_row, tournament_id=1)
    
    def test_csv_row_parsing_empty_team_name(self, team_service):
        """Test CSV row parsing with empty team name."""
        csv_row = {
            "Team": "",  # Empty team name
            "Email": "test@example.com"
        }
        
        with pytest.raises(ValueError, match="Team name is required"):
            team_service._parse_csv_row(csv_row, tournament_id=1)
    
    def test_team_update_validation(self, team_service):
        """Test team update validation."""
        from schemas import TeamUpdate
        
        # Test valid update data
        valid_update = TeamUpdate(name="Updated Team Name")
        validation_result = team_service.validation_service.validate_team_update(valid_update)
        assert validation_result.is_valid is True
        
        # Test invalid update data
        invalid_update = TeamUpdate(email="invalid-email")  # Invalid email format
        validation_result = team_service.validation_service.validate_team_update(invalid_update)
        assert validation_result.is_valid is False
        assert "Email must be a valid email address" in validation_result.errors
    
    def test_robot_update_validation(self, team_service):
        """Test robot update validation."""
        from schemas import RobotUpdate
        
        # Test valid update data
        valid_update = RobotUpdate(name="Updated Robot Name")
        validation_result = team_service.validation_service.validate_robot_update(valid_update)
        assert validation_result.is_valid is True
        
        # Test invalid update data - test with comments that are too long
        invalid_update = RobotUpdate(comments="x" * 1001)  # Comments too long
        validation_result = team_service.validation_service.validate_robot_update(invalid_update)
        assert validation_result.is_valid is False
        assert "Robot comments must be 1000 characters or less" in validation_result.errors
    
    def test_player_update_validation(self, team_service):
        """Test player update validation."""
        from schemas import PlayerUpdate
        
        # Test valid update data
        valid_update = PlayerUpdate(first_name="Updated", last_name="Player")
        validation_result = team_service.validation_service.validate_player_update(valid_update)
        assert validation_result.is_valid is True
        
        # Test invalid update data
        invalid_update = PlayerUpdate(email="invalid-email")  # Invalid email format
        validation_result = team_service.validation_service.validate_player_update(invalid_update)
        assert validation_result.is_valid is False
        assert "Player email must be a valid email address" in validation_result.errors
