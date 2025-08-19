"""
Simplified unit tests for MatchService
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from services.match_service import MatchService
from schemas import SwissMatchCreate, SwissMatchUpdate, EliminationMatchCreate, EliminationMatchUpdate
from models import MatchStatus, Team, SwissRound, EliminationBracket


class TestMatchServiceSimple:
    """Simplified test cases for MatchService."""
    
    @pytest.fixture
    def match_service(self, test_settings):
        """Create MatchService instance."""
        return MatchService(test_settings)
    
    def test_match_service_initialization(self, match_service):
        """Test that MatchService initializes correctly."""
        assert match_service is not None
        assert match_service.settings is not None
        assert match_service.validation_service is not None
    
    def test_validation_service_integration(self, match_service):
        """Test that MatchService uses ValidationService correctly."""
        # Test with valid match data
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2
        )
        
        # This should not raise an error
        validation_result = match_service.validation_service.validate_match_data(match_data)
        assert validation_result.is_valid is True
    
    def test_validation_service_invalid_data(self, match_service):
        """Test validation with invalid match data."""
        # Test with same team IDs (invalid)
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=1  # Same team
        )
        
        validation_result = match_service.validation_service.validate_match_data(match_data)
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0
    
    def test_match_result_validation(self, match_service):
        """Test match result validation."""
        # Valid result
        winner_id = 1
        scores = {"team1_score": 3, "team2_score": 1}
        
        validation_result = match_service.validation_service.validate_match_result(winner_id, scores)
        assert validation_result.is_valid is True
    
    def test_match_result_validation_tie(self, match_service):
        """Test match result validation with tie."""
        # Invalid result - tie
        winner_id = 1
        scores = {"team1_score": 3, "team2_score": 3}  # Tie
        
        validation_result = match_service.validation_service.validate_match_result(winner_id, scores)
        assert validation_result.is_valid is False
        assert "Match cannot end in a tie" in validation_result.errors[0]
    
    def test_match_result_validation_winner_mismatch(self, match_service):
        """Test match result validation with winner mismatch."""
        # Invalid result - winner doesn't match scores
        winner_id = 1
        scores = {"team1_score": 1, "team2_score": 3}  # Team 2 scored higher
        
        validation_result = match_service.validation_service.validate_match_result(winner_id, scores)
        assert validation_result.is_valid is False
        assert "Winner ID does not match scores" in validation_result.errors[0]
    
    def test_elimination_match_validation(self, match_service):
        """Test elimination match data validation."""
        # Valid elimination match data
        match_data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1,
            match_number=1
        )
        
        validation_result = match_service.validation_service.validate_elimination_match_data(match_data)
        assert validation_result.is_valid is True
    
    def test_elimination_match_validation_invalid_round(self, match_service):
        """Test elimination match validation with invalid round."""
        # Invalid round number
        match_data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=1,
            team2_id=2,
            round_number=0,  # Invalid
            match_number=1
        )
        
        validation_result = match_service.validation_service.validate_elimination_match_data(match_data)
        assert validation_result.is_valid is False
        assert "Round number must be at least 1" in validation_result.errors[0]
    
    def test_match_status_enum_values(self):
        """Test that MatchStatus enum has expected values."""
        assert MatchStatus.SCHEDULED.value == "scheduled"
        assert MatchStatus.IN_PROGRESS.value == "in_progress"
        assert MatchStatus.COMPLETED.value == "completed"
        assert MatchStatus.CANCELLED.value == "cancelled"
        assert MatchStatus.DELAYED.value == "delayed"
    
    def test_swiss_match_create_schema(self):
        """Test SwissMatchCreate schema validation."""
        # Valid data
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2
        )
        
        assert match_data.swiss_round_id == 1
        assert match_data.team1_id == 1
        assert match_data.team2_id == 2
    
    def test_elimination_match_create_schema(self):
        """Test EliminationMatchCreate schema validation."""
        # Valid data
        match_data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1,
            match_number=1
        )
        
        assert match_data.bracket_id == 1
        assert match_data.team1_id == 1
        assert match_data.team2_id == 2
        assert match_data.round_number == 1
        assert match_data.match_number == 1
    
    def test_swiss_match_update_schema(self):
        """Test SwissMatchUpdate schema validation."""
        # Valid update data
        update_data = SwissMatchUpdate(
            winner_id=1,
            scores={"team1_score": 3, "team2_score": 1},
            status=MatchStatus.COMPLETED
        )
        
        assert update_data.winner_id == 1
        assert update_data.scores == {"team1_score": 3, "team2_score": 1}
        assert update_data.status == MatchStatus.COMPLETED
    
    def test_elimination_match_update_schema(self):
        """Test EliminationMatchUpdate schema validation."""
        # Valid update data
        update_data = EliminationMatchUpdate(
            winner_id=2,
            scores={"team1_score": 1, "team2_score": 3},
            status=MatchStatus.COMPLETED
        )
        
        assert update_data.winner_id == 2
        assert update_data.scores == {"team1_score": 1, "team2_score": 3}
        assert update_data.status == MatchStatus.COMPLETED
