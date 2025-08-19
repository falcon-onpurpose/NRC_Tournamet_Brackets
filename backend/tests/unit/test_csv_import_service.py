"""
Unit tests for CSV Import Service.
Tests comprehensive CSV import validation and data sanitization.
"""

import pytest
from services.csv_import_service import CSVImportService, ImportSeverity


class TestCSVImportService:
    """Tests for CSVImportService functionality."""
    
    @pytest.fixture
    def csv_import_service(self, test_settings):
        return CSVImportService(test_settings)
    
    def test_csv_import_service_initialization(self, csv_import_service):
        """Test CSVImportService initializes correctly."""
        assert csv_import_service is not None
        assert csv_import_service.settings is not None
        assert csv_import_service.validation_service is not None
        assert csv_import_service.field_limits is not None
        assert csv_import_service.robot_class_mappings is not None
    
    def test_import_valid_data(self, csv_import_service):
        """Test importing valid CSV data."""
        csv_data = [
            {
                "Team": "Test Team",
                "Team_Address": "123 Test St",
                "Team_Phone": "123-456-7890",
                "Robot_Name": "Test Robot",
                "Robot_Weightclass": "150g - Non-Destructive",
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "John",
                "Last_Name": "Doe",
                "Email": "john@example.com",
                "Comments": "Test comment"
            }
        ]
        
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
        
        assert result.success is True
        assert result.total_rows == 1
        assert result.processed_rows == 1
        assert result.successful_imports == 1
        assert len(result.teams_created) == 1
        assert len(result.robots_created) == 1
        assert len(result.players_created) == 1
        assert len(result.errors) == 0
    
    def test_string_length_clipping(self, csv_import_service):
        """Test string length clipping functionality."""
        csv_data = [
            {
                "Team": "x" * 150,  # Too long, should be clipped to 100
                "Team_Address": "123 Test St",
                "Team_Phone": "123-456-7890",
                "Robot_Name": "y" * 150,  # Too long, should be clipped to 100
                "Robot_Weightclass": "150g - Non-Destructive",
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "z" * 80,  # Too long, should be clipped to 50
                "Last_Name": "w" * 80,  # Too long, should be clipped to 50
                "Email": "test@example.com",
                "Comments": "c" * 1200  # Too long, should be clipped to 1000
            }
        ]
        
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
        
        assert result.success is True
        assert len(result.warnings) >= 4  # Should have warnings for clipped fields
        
        # Check that data was clipped correctly
        team = result.teams_created[0]
        robot = result.robots_created[0]
        player = result.players_created[0]
        
        assert len(team["name"]) == 100
        assert len(robot["name"]) == 100
        assert len(player["first_name"]) == 50
        assert len(player["last_name"]) == 50
        assert len(robot["comments"]) == 1000
    
    def test_data_sanitization(self, csv_import_service):
        """Test data sanitization functionality."""
        csv_data = [
            {
                "Team": "  Test<script>alert('xss')</script>Team  ",
                "Team_Address": "123 Test St\n\nwith\twhitespace",
                "Team_Phone": "123-456-7890",
                "Robot_Name": "Robot\"Name'With'Quotes",
                "Robot_Weightclass": "150g - Non-Destructive",
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "John\x00\x08",  # Control characters
                "Last_Name": "Doe",
                "Email": "test@example.com",
                "Comments": "Comment with <b>HTML</b> tags"
            }
        ]
        
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
        
        assert result.success is True
        
        # Check that data was sanitized
        team = result.teams_created[0]
        robot = result.robots_created[0]
        player = result.players_created[0]
        
        assert "<script>" not in team["name"]
        assert "&lt;script&gt;" in team["name"]  # Should be HTML escaped
        assert "alert" in team["name"]  # Content preserved but escaped
        assert "\n" not in team["address"]
        assert "\t" not in team["address"]
        assert "\"" not in robot["name"]
        assert "'" not in robot["name"]
        assert "\x00" not in player["first_name"]
        assert "\x08" not in player["first_name"]
        assert "<b>" not in robot["comments"]
        assert "</b>" not in robot["comments"]
    
    def test_email_validation(self, csv_import_service):
        """Test email validation and normalization."""
        csv_data = [
            {
                "Team": "Test Team",
                "Team_Address": "123 Test St",
                "Team_Phone": "123-456-7890",
                "Robot_Name": "Test Robot",
                "Robot_Weightclass": "150g - Non-Destructive",
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "John",
                "Last_Name": "Doe",
                "Email": "INVALID-EMAIL-FORMAT",  # Invalid email
                "Comments": ""
            }
        ]
        
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
        
        assert result.success is True
        assert len(result.warnings) >= 1  # Should have warning for invalid email
        
        # Email should be None due to validation failure
        player = result.players_created[0]
        assert player["email"] is None
    
    def test_phone_sanitization(self, csv_import_service):
        """Test phone number sanitization."""
        csv_data = [
            {
                "Team": "Test Team",
                "Team_Address": "123 Test St",
                "Team_Phone": "+1 (555) 123-4567 ext. 890",  # Complex phone format
                "Robot_Name": "Test Robot",
                "Robot_Weightclass": "150g - Non-Destructive",
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "John",
                "Last_Name": "Doe",
                "Email": "test@example.com",
                "Comments": ""
            }
        ]
        
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
        
        assert result.success is True
        
        team = result.teams_created[0]
        # Should keep digits, +, spaces, (), - but remove "ext."
        assert "ext" not in team["phone"]
        assert "+" in team["phone"]
        assert "555" in team["phone"]
    
    def test_boolean_parsing(self, csv_import_service):
        """Test boolean field parsing."""
        test_cases = [
            ("true", True),
            ("false", False),
            ("1", True),
            ("0", False),
            ("yes", True),
            ("no", False),
            ("invalid", False),  # Should default to False with warning
            ("", False)
        ]
        
        for bool_str, expected in test_cases:
            csv_data = [
                {
                    "Team": "Test Team",
                    "Team_Address": "123 Test St",
                    "Team_Phone": "123-456-7890",
                    "Robot_Name": "Test Robot",
                    "Robot_Weightclass": "150g - Non-Destructive",
                    "Waitlist": bool_str,
                    "Robot_Fee_Paid": "false",
                    "First_Name": "John",
                    "Last_Name": "Doe",
                    "Email": "test@example.com",
                    "Comments": ""
                }
            ]
            
            result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
            
            assert result.success is True
            robot = result.robots_created[0]
            assert robot["waitlist"] == expected
    
    def test_robot_class_mapping(self, csv_import_service):
        """Test robot class mapping functionality."""
        valid_classes = [
            "150g - Non-Destructive",
            "150g - Antweight Destructive", 
            "150g - Destructive",
            "Beetleweight"
        ]
        
        for robot_class in valid_classes:
            csv_data = [
                {
                    "Team": "Test Team",
                    "Team_Address": "123 Test St",
                    "Team_Phone": "123-456-7890",
                    "Robot_Name": "Test Robot",
                    "Robot_Weightclass": robot_class,
                    "Waitlist": "false",
                    "Robot_Fee_Paid": "true",
                    "First_Name": "John",
                    "Last_Name": "Doe",
                    "Email": "test@example.com",
                    "Comments": ""
                }
            ]
            
            result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
            
            assert result.success is True
            assert len(result.robots_created) == 1
            robot = result.robots_created[0]
            assert robot["robot_class_id"] is not None
            assert robot["robot_class_id"] > 0
    
    def test_invalid_robot_class(self, csv_import_service):
        """Test handling of invalid robot class."""
        csv_data = [
            {
                "Team": "Test Team",
                "Team_Address": "123 Test St",
                "Team_Phone": "123-456-7890",
                "Robot_Name": "Test Robot",
                "Robot_Weightclass": "Invalid Class",  # Invalid robot class
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "John",
                "Last_Name": "Doe",
                "Email": "test@example.com",
                "Comments": ""
            }
        ]
        
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
        
        assert len(result.errors) >= 1  # Should have error for invalid robot class
        assert len(result.robots_created) == 0  # No robot should be created
    
    def test_missing_required_fields(self, csv_import_service):
        """Test handling of missing required fields."""
        csv_data = [
            {
                "Team": "",  # Missing team name
                "Team_Address": "123 Test St",
                "Team_Phone": "123-456-7890",
                "Robot_Name": "",  # Missing robot name
                "Robot_Weightclass": "150g - Non-Destructive",
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "",  # Missing first name
                "Last_Name": "Doe",
                "Email": "test@example.com",
                "Comments": ""
            }
        ]
        
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
        
        assert len(result.errors) >= 3  # Should have errors for missing fields
        assert len(result.teams_created) == 0
        assert len(result.robots_created) == 0
        assert len(result.players_created) == 0
    
    def test_duplicate_handling(self, csv_import_service):
        """Test handling of duplicate entries."""
        csv_data = [
            {
                "Team": "Test Team",
                "Team_Address": "123 Test St",
                "Team_Phone": "123-456-7890",
                "Robot_Name": "Test Robot",
                "Robot_Weightclass": "150g - Non-Destructive",
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "John",
                "Last_Name": "Doe",
                "Email": "test@example.com",
                "Comments": ""
            },
            {
                "Team": "Test Team",  # Duplicate team
                "Team_Address": "456 Other St",
                "Team_Phone": "098-765-4321",
                "Robot_Name": "Test Robot",  # Duplicate robot in same team
                "Robot_Weightclass": "150g - Non-Destructive",
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "John",  # Duplicate player
                "Last_Name": "Doe",
                "Email": "john2@example.com",
                "Comments": ""
            }
        ]
        
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
        
        assert result.success is True
        assert result.total_rows == 2
        assert result.processed_rows == 2
        
        # Should only create one of each due to duplicate detection
        assert len(result.teams_created) == 1
        assert len(result.robots_created) == 1
        assert len(result.players_created) == 1
    
    def test_strict_mode(self, csv_import_service):
        """Test strict mode behavior."""
        csv_data = [
            {
                "Team": "Test Team",
                "Team_Address": "123 Test St",
                "Team_Phone": "123-456-7890",
                "Robot_Name": "Test Robot",
                "Robot_Weightclass": "Invalid Class",  # This will cause an error
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "John",
                "Last_Name": "Doe",
                "Email": "test@example.com",
                "Comments": ""
            }
        ]
        
        # Test strict mode
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1, strict_mode=True)
        assert result.success is False  # Should fail in strict mode
        
        # Test non-strict mode
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1, strict_mode=False)
        assert result.success is True  # Should succeed in non-strict mode despite errors
    
    def test_import_report_generation(self, csv_import_service):
        """Test import report generation."""
        csv_data = [
            {
                "Team": "Test Team",
                "Team_Address": "123 Test St",
                "Team_Phone": "123-456-7890",
                "Robot_Name": "Test Robot",
                "Robot_Weightclass": "150g - Non-Destructive",
                "Waitlist": "false",
                "Robot_Fee_Paid": "true",
                "First_Name": "John",
                "Last_Name": "Doe",
                "Email": "invalid-email",  # This will cause a warning
                "Comments": ""
            }
        ]
        
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
        report = csv_import_service.generate_import_report(result)
        
        assert isinstance(report, str)
        assert "CSV Import Report" in report
        assert "Total rows processed: 1" in report
        assert "Teams created: 1" in report
        assert "Robots created: 1" in report
        assert "Players created: 1" in report
        assert "WARNINGS:" in report
    
    def test_edge_cases(self, csv_import_service):
        """Test various edge cases."""
        # Test empty CSV data
        result = csv_import_service.import_tournament_data([], tournament_id=1)
        assert result.success is True
        assert result.total_rows == 0
        assert result.processed_rows == 0
        
        # Test CSV data with None values
        csv_data = [
            {
                "Team": None,
                "Team_Address": None,
                "Team_Phone": None,
                "Robot_Name": None,
                "Robot_Weightclass": None,
                "Waitlist": None,
                "Robot_Fee_Paid": None,
                "First_Name": None,
                "Last_Name": None,
                "Email": None,
                "Comments": None
            }
        ]
        
        result = csv_import_service.import_tournament_data(csv_data, tournament_id=1)
        assert len(result.errors) >= 3  # Should have errors for missing required fields
