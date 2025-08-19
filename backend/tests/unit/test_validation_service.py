"""
Unit tests for validation service.
"""
import pytest
from datetime import datetime, timedelta

from services.validation_service import ValidationService, ValidationResult
from schemas import TournamentCreate, TournamentUpdate, SwissMatchCreate, EliminationMatchCreate


class TestValidationService:
    """Test validation service functionality."""
    
    @pytest.fixture
    def validation_service(self):
        """Create validation service instance."""
        return ValidationService()
    
    def test_validate_tournament_data_success(self, validation_service):
        """Test successful tournament data validation."""
        # Arrange
        data = TournamentCreate(
            name="Valid Tournament",
            format="hybrid_swiss_elimination",
            location="Valid Arena",
            description="Valid description",
            swiss_rounds_count=3,
            start_date=datetime.utcnow() + timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=2)
        )
        
        # Act
        result = validation_service.validate_tournament_data(data)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_tournament_data_empty_name(self, validation_service):
        """Test tournament data validation with empty name."""
        # Arrange
        data = TournamentCreate(
            name="",
            format="hybrid_swiss_elimination",
            location="Valid Arena",
            description="Valid description",
            swiss_rounds_count=3,
            start_date=datetime.utcnow() + timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=2)
        )
        
        # Act
        result = validation_service.validate_tournament_data(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "name is required" in result.errors[0]
    
    def test_validate_tournament_data_invalid_format(self, validation_service):
        """Test tournament data validation with invalid format."""
        # Arrange
        data = TournamentCreate(
            name="Valid Tournament",
            format="invalid_format",
            location="Valid Arena",
            description="Valid description",
            swiss_rounds=3,
            start_date=datetime.utcnow() + timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=2)
        )
        
        # Act
        result = validation_service.validate_tournament_data(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Invalid tournament format" in result.errors[0]
    
    def test_validate_tournament_data_invalid_swiss_rounds(self, validation_service):
        """Test tournament data validation with invalid Swiss rounds."""
        # Arrange
        data = TournamentCreate(
            name="Valid Tournament",
            format="hybrid_swiss_elimination",
            location="Valid Arena",
            description="Valid description",
            swiss_rounds_count=0,  # Invalid: zero rounds
            start_date=datetime.utcnow() + timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=2)
        )
        
        # Act
        result = validation_service.validate_tournament_data(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Swiss rounds must be at least 1" in result.errors[0]
    
    def test_validate_tournament_data_invalid_dates(self, validation_service):
        """Test tournament data validation with invalid dates."""
        # Arrange
        data = TournamentCreate(
            name="Valid Tournament",
            format="hybrid_swiss_elimination",
            location="Valid Arena",
            description="Valid description",
            swiss_rounds_count=3,
            start_date=datetime.utcnow() + timedelta(days=2),
            end_date=datetime.utcnow() + timedelta(days=1)  # End before start
        )
        
        # Act
        result = validation_service.validate_tournament_data(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Start date must be before end date" in result.errors[0]
    
    def test_validate_tournament_data_past_start_date(self, validation_service):
        """Test tournament data validation with past start date."""
        # Arrange
        data = TournamentCreate(
            name="Valid Tournament",
            format="hybrid_swiss_elimination",
            location="Valid Arena",
            description="Valid description",
            swiss_rounds_count=3,
            start_date=datetime.utcnow() - timedelta(days=1),  # Past date
            end_date=datetime.utcnow() + timedelta(days=1)
        )
        
        # Act
        result = validation_service.validate_tournament_data(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Start date cannot be in the past" in result.errors[0]
    
    def test_validate_tournament_update_success(self, validation_service):
        """Test successful tournament update validation."""
        # Arrange
        data = TournamentUpdate(name="Updated Tournament")
        
        # Act
        result = validation_service.validate_tournament_update(data)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_tournament_update_empty_name(self, validation_service):
        """Test tournament update validation with empty name."""
        # Arrange
        data = TournamentUpdate(name="")
        
        # Act
        result = validation_service.validate_tournament_update(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "name cannot be empty" in result.errors[0]
    
    def test_validate_match_data_success(self, validation_service):
        """Test successful match data validation."""
        # Arrange
        data = SwissMatchCreate(
            tournament_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1
        )
        
        # Act
        result = validation_service.validate_match_data(data)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_match_data_same_team(self, validation_service):
        """Test match data validation with same team."""
        # Arrange
        data = SwissMatchCreate(
            tournament_id=1,
            team1_id=1,
            team2_id=1,  # Same as team1_id
            round_number=1
        )
        
        # Act
        result = validation_service.validate_match_data(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "must be different teams" in result.errors[0]
    
    def test_validate_match_data_invalid_round(self, validation_service):
        """Test match data validation with invalid round number."""
        # Arrange
        data = SwissMatchCreate(
            tournament_id=1,
            team1_id=1,
            team2_id=2,
            round_number=0  # Invalid: zero round
        )
        
        # Act
        result = validation_service.validate_match_data(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Round number must be at least 1" in result.errors[0]
    
    def test_validate_elimination_match_data_success(self, validation_service):
        """Test successful elimination match data validation."""
        # Arrange
        data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1,
            match_number=1
        )
        
        # Act
        result = validation_service.validate_elimination_match_data(data)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_elimination_match_data_invalid_match_number(self, validation_service):
        """Test elimination match data validation with invalid match number."""
        # Arrange
        data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1,
            match_number=0  # Invalid: zero match number
        )
        
        # Act
        result = validation_service.validate_elimination_match_data(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Match number must be at least 1" in result.errors[0]
    
    def test_validate_team_data_success(self, validation_service):
        """Test successful team data validation."""
        # Arrange
        from schemas import TeamCreate
        data = TeamCreate(
            name="Valid Team",
            address="Valid Address",
            phone="1234567890",
            email="team@example.com"
        )
        
        # Act
        result = validation_service.validate_team_data(data)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_team_data_missing_name(self, validation_service):
        """Test team data validation with missing name."""
        # This test is no longer valid since Pydantic validates required fields
        # We'll test with an address that's too long instead
        from schemas import TeamCreate
        
        # Arrange
        data = TeamCreate(
            name="Valid Team",
            address="x" * 501,  # Address too long (max 500)
            phone="1234567890",
            email="team@example.com"
        )
        
        # Act
        result = validation_service.validate_team_data(data)
        
        # Assert
        assert result.is_valid is False
        assert "Address must be 500 characters or less" in result.errors
    
    def test_validate_team_data_invalid_email(self, validation_service):
        """Test team data validation with invalid email."""
        # Arrange
        from schemas import TeamCreate
        data = TeamCreate(
            name="Valid Team",
            address="Valid Address",
            phone="1234567890",
            email="invalid-email"  # Invalid email format
        )
        
        # Act
        result = validation_service.validate_team_data(data)
        
        # Assert
        assert result.is_valid is False
        assert "Email must be a valid email address" in result.errors
    
    def test_validate_robot_data_success(self, validation_service):
        """Test successful robot data validation."""
        # Arrange
        from schemas import RobotCreate
        data = RobotCreate(
            name="Valid Robot",
            robot_class_id=1
        )
        
        # Act
        result = validation_service.validate_robot_data(data)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_robot_data_missing_name(self, validation_service):
        """Test robot data validation with missing name."""
        # This test is no longer valid since Pydantic validates required fields
        # We'll test with comments that are too long instead
        from schemas import RobotCreate
        
        # Arrange
        data = RobotCreate(
            name="Valid Robot",
            robot_class_id=1,
            comments="x" * 1001  # Comments too long (max 1000)
        )
        
        # Act
        result = validation_service.validate_robot_data(data)
        
        # Assert
        assert result.is_valid is False
        assert "Robot comments must be 1000 characters or less" in result.errors
    
    def test_validate_robot_data_invalid_weight(self, validation_service):
        """Test robot data validation with invalid robot class ID."""
        # Arrange
        from schemas import RobotCreate
        data = RobotCreate(
            name="Valid Robot",
            robot_class_id=0  # Invalid robot class ID
        )
        
        # Act
        result = validation_service.validate_robot_data(data)
        
        # Assert
        assert result.is_valid is False
        assert "Valid robot class ID is required" in result.errors
    
    def test_validate_csv_import_data_success(self, validation_service):
        """Test successful CSV import data validation."""
        # Arrange
        csv_data = """Team,Robot_Name,Robot_Weightclass,Team_Address,Team_Phone,First_Name,Last_Name,Email
Team Alpha,Alpha Bot,150g - Non-Destructive,123 Test St,1234567890,John,Doe,john@example.com
Team Beta,Beta Bot,150g - Destructive,456 Test Ave,0987654321,Jane,Smith,jane@example.com"""
        
        # Act
        result = validation_service.validate_csv_import_data(csv_data)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_csv_import_data_missing_headers(self, validation_service):
        """Test CSV import data validation with missing headers."""
        # Arrange
        csv_data = """Team,Robot_Name,Team_Address,Team_Phone,First_Name,Last_Name,Email
Team Alpha,Alpha Bot,123 Test St,1234567890,John,Doe,john@example.com"""
        # Missing Robot_Weightclass header
        
        # Act
        result = validation_service.validate_csv_import_data(csv_data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Missing required headers" in result.errors[0]
    
    def test_validate_csv_import_data_empty(self, validation_service):
        """Test CSV import data validation with empty data."""
        # Arrange
        csv_data = ""
        
        # Act
        result = validation_service.validate_csv_import_data(csv_data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "CSV data is required" in result.errors[0]
    
    def test_validate_match_result_success(self, validation_service):
        """Test successful match result validation."""
        # Arrange
        winner_id = 1
        scores = {"team1_score": 3, "team2_score": 1}
        
        # Act
        result = validation_service.validate_match_result(winner_id, scores)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_match_result_missing_scores(self, validation_service):
        """Test match result validation with missing scores."""
        # Arrange
        winner_id = 1
        scores = {}
        
        # Act
        result = validation_service.validate_match_result(winner_id, scores)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Match scores are required" in result.errors[0]
    
    def test_validate_match_result_tie(self, validation_service):
        """Test match result validation with tie scores."""
        # Arrange
        winner_id = 1
        scores = {"team1_score": 3, "team2_score": 3}  # Tie
        
        # Act
        result = validation_service.validate_match_result(winner_id, scores)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "cannot end in a tie" in result.errors[0]
    
    def test_validate_match_result_winner_mismatch(self, validation_service):
        """Test match result validation with winner mismatch."""
        # Arrange
        winner_id = 1  # Team 1 wins
        scores = {"team1_score": 1, "team2_score": 3}  # But team 2 has higher score
        
        # Act
        result = validation_service.validate_match_result(winner_id, scores)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Winner ID does not match scores" in result.errors[0]
    
    def test_validate_match_result_invalid_winner_id(self, validation_service):
        """Test match result validation with invalid winner ID."""
        # Arrange
        winner_id = 0  # Invalid: zero ID
        scores = {"team1_score": 3, "team2_score": 1}
        
        # Act
        result = validation_service.validate_match_result(winner_id, scores)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Invalid winner ID" in result.errors[0]
