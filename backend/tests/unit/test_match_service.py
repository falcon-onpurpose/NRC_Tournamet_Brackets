"""
Unit tests for MatchService
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from services.match_service import MatchService
from schemas import SwissMatchCreate, SwissMatchUpdate, EliminationMatchCreate, EliminationMatchUpdate
from models import MatchStatus, Team, SwissRound, EliminationBracket


class TestMatchService:
    """Test cases for MatchService."""
    
    @pytest.fixture
    def match_service(self, test_settings):
        """Create MatchService instance."""
        return MatchService(test_settings)
    
    @pytest.fixture
    def sample_teams(self):
        """Sample teams for testing."""
        return [
            Team(id=1, name="Team Alpha", tournament_id=1),
            Team(id=2, name="Team Beta", tournament_id=1),
            Team(id=3, name="Team Gamma", tournament_id=1),
            Team(id=4, name="Team Delta", tournament_id=1)
        ]
    
    @pytest.fixture
    def sample_swiss_round(self):
        """Sample Swiss round for testing."""
        return SwissRound(id=1, tournament_id=1, robot_class_id=1, round_number=1)
    
    @pytest.fixture
    def sample_elimination_bracket(self):
        """Sample elimination bracket for testing."""
        return EliminationBracket(id=1, tournament_id=1, robot_class_id=1, bracket_type="winners")
    
    @pytest.mark.asyncio
    async def test_create_swiss_match_success(self, match_service, test_session, sample_teams, sample_swiss_round):
        """Test successful Swiss match creation."""
        # Arrange
        async with test_session as session:
            for team in sample_teams:
                session.add(team)
            session.add(sample_swiss_round)
            session.commit()
        
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2,
            scheduled_time=datetime.utcnow() + timedelta(hours=1)
        )
        
        # Act
        async with test_session as session:
            result = await match_service.create_swiss_match(session, match_data)
            
            # Assert
            assert result is not None
            assert result.team1_id == 1
            assert result.team2_id == 2
            assert result.team1_name == "Team Alpha"
            assert result.team2_name == "Team Beta"
            assert result.status == MatchStatus.SCHEDULED
            assert result.swiss_round_id == 1
    
    @pytest.mark.asyncio
    async def test_create_swiss_match_invalid_teams(self, match_service, test_session):
        """Test Swiss match creation with invalid team IDs."""
        # Arrange
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=999,  # Non-existent team
            team2_id=2
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="One or both teams not found"):
            await match_service.create_swiss_match(test_session, match_data)
    
    @pytest.mark.asyncio
    async def test_get_swiss_match_success(self, match_service, test_session, sample_teams, sample_swiss_round):
        """Test successful Swiss match retrieval."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_swiss_round)
        test_session.commit()
        
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2
        )
        created_match = await match_service.create_swiss_match(test_session, match_data)
        
        # Act
        result = await match_service.get_swiss_match(test_session, created_match.id)
        
        # Assert
        assert result is not None
        assert result.id == created_match.id
        assert result.team1_name == "Team Alpha"
        assert result.team2_name == "Team Beta"
    
    @pytest.mark.asyncio
    async def test_get_swiss_match_not_found(self, match_service, test_session):
        """Test Swiss match retrieval with non-existent ID."""
        # Act
        result = await match_service.get_swiss_match(test_session, 999)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_start_swiss_match_success(self, match_service, test_session, sample_teams, sample_swiss_round):
        """Test successful Swiss match start."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_swiss_round)
        test_session.commit()
        
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2
        )
        created_match = await match_service.create_swiss_match(test_session, match_data)
        
        # Act
        result = await match_service.start_swiss_match(test_session, created_match.id)
        
        # Assert
        assert result is not None
        assert result.status == MatchStatus.IN_PROGRESS
        assert result.start_time is not None
    
    @pytest.mark.asyncio
    async def test_start_swiss_match_wrong_status(self, match_service, test_session, sample_teams, sample_swiss_round):
        """Test starting Swiss match with wrong status."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_swiss_round)
        test_session.commit()
        
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2
        )
        created_match = await match_service.create_swiss_match(test_session, match_data)
        
        # Start the match first
        await match_service.start_swiss_match(test_session, created_match.id)
        
        # Act & Assert - Try to start again
        with pytest.raises(ValueError, match="Match is not in scheduled status"):
            await match_service.start_swiss_match(test_session, created_match.id)
    
    @pytest.mark.asyncio
    async def test_complete_swiss_match_success(self, match_service, test_session, sample_teams, sample_swiss_round):
        """Test successful Swiss match completion."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_swiss_round)
        test_session.commit()
        
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2
        )
        created_match = await match_service.create_swiss_match(test_session, match_data)
        await match_service.start_swiss_match(test_session, created_match.id)
        
        # Act
        result = await match_service.complete_swiss_match(
            test_session, 
            created_match.id, 
            winner_id=1, 
            scores={"team1_score": 3, "team2_score": 1}
        )
        
        # Assert
        assert result is not None
        assert result.status == MatchStatus.COMPLETED
        assert result.winner_id == 1
        assert result.scores == {"team1_score": 3, "team2_score": 1}
        assert result.end_time is not None
    
    @pytest.mark.asyncio
    async def test_complete_swiss_match_invalid_result(self, match_service, test_session, sample_teams, sample_swiss_round):
        """Test Swiss match completion with invalid result."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_swiss_round)
        test_session.commit()
        
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2
        )
        created_match = await match_service.create_swiss_match(test_session, match_data)
        await match_service.start_swiss_match(test_session, created_match.id)
        
        # Act & Assert - Tie scores
        with pytest.raises(ValueError, match="Invalid match result"):
            await match_service.complete_swiss_match(
                test_session, 
                created_match.id, 
                winner_id=1, 
                scores={"team1_score": 3, "team2_score": 3}  # Tie
            )
    
    @pytest.mark.asyncio
    async def test_create_elimination_match_success(self, match_service, test_session, sample_teams, sample_elimination_bracket):
        """Test successful elimination match creation."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_elimination_bracket)
        test_session.commit()
        
        match_data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1,
            match_number=1
        )
        
        # Act
        result = await match_service.create_elimination_match(test_session, match_data)
        
        # Assert
        assert result is not None
        assert result.team1_id == 1
        assert result.team2_id == 2
        assert result.team1_name == "Team Alpha"
        assert result.team2_name == "Team Beta"
        assert result.status == MatchStatus.SCHEDULED
        assert result.bracket_id == 1
        assert result.round_number == 1
        assert result.match_number == 1
    
    @pytest.mark.asyncio
    async def test_get_elimination_match_success(self, match_service, test_session, sample_teams, sample_elimination_bracket):
        """Test successful elimination match retrieval."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_elimination_bracket)
        test_session.commit()
        
        match_data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1,
            match_number=1
        )
        created_match = await match_service.create_elimination_match(test_session, match_data)
        
        # Act
        result = await match_service.get_elimination_match(test_session, created_match.id)
        
        # Assert
        assert result is not None
        assert result.id == created_match.id
        assert result.team1_name == "Team Alpha"
        assert result.team2_name == "Team Beta"
    
    @pytest.mark.asyncio
    async def test_start_elimination_match_success(self, match_service, test_session, sample_teams, sample_elimination_bracket):
        """Test successful elimination match start."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_elimination_bracket)
        test_session.commit()
        
        match_data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1,
            match_number=1
        )
        created_match = await match_service.create_elimination_match(test_session, match_data)
        
        # Act
        result = await match_service.start_elimination_match(test_session, created_match.id)
        
        # Assert
        assert result is not None
        assert result.status == MatchStatus.IN_PROGRESS
        assert result.start_time is not None
    
    @pytest.mark.asyncio
    async def test_complete_elimination_match_success(self, match_service, test_session, sample_teams, sample_elimination_bracket):
        """Test successful elimination match completion."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_elimination_bracket)
        test_session.commit()
        
        match_data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1,
            match_number=1
        )
        created_match = await match_service.create_elimination_match(test_session, match_data)
        await match_service.start_elimination_match(test_session, created_match.id)
        
        # Act
        result = await match_service.complete_elimination_match(
            test_session, 
            created_match.id, 
            winner_id=2, 
            scores={"team1_score": 1, "team2_score": 3}
        )
        
        # Assert
        assert result is not None
        assert result.status == MatchStatus.COMPLETED
        assert result.winner_id == 2
        assert result.scores == {"team1_score": 1, "team2_score": 3}
        assert result.end_time is not None
    
    @pytest.mark.asyncio
    async def test_get_pending_matches(self, match_service, test_session, sample_teams, sample_swiss_round, sample_elimination_bracket):
        """Test getting pending matches for a tournament."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_swiss_round)
        test_session.add(sample_elimination_bracket)
        test_session.commit()
        
        # Create some matches
        swiss_match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2
        )
        await match_service.create_swiss_match(test_session, swiss_match_data)
        
        elimination_match_data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=3,
            team2_id=4,
            round_number=1,
            match_number=1
        )
        await match_service.create_elimination_match(test_session, elimination_match_data)
        
        # Act
        result = await match_service.get_pending_matches(test_session, tournament_id=1)
        
        # Assert
        assert "swiss_matches" in result
        assert "elimination_matches" in result
        assert len(result["swiss_matches"]) == 1
        assert len(result["elimination_matches"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_match_statistics(self, match_service, test_session, sample_teams, sample_swiss_round, sample_elimination_bracket):
        """Test getting match statistics for a tournament."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_swiss_round)
        test_session.add(sample_elimination_bracket)
        test_session.commit()
        
        # Create and complete some matches
        swiss_match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2
        )
        created_swiss = await match_service.create_swiss_match(test_session, swiss_match_data)
        await match_service.start_swiss_match(test_session, created_swiss.id)
        await match_service.complete_swiss_match(
            test_session, 
            created_swiss.id, 
            winner_id=1, 
            scores={"team1_score": 3, "team2_score": 1}
        )
        
        elimination_match_data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=3,
            team2_id=4,
            round_number=1,
            match_number=1
        )
        await match_service.create_elimination_match(test_session, elimination_match_data)
        
        # Act
        result = await match_service.get_match_statistics(test_session, tournament_id=1)
        
        # Assert
        assert "swiss_matches" in result
        assert "elimination_matches" in result
        assert result["swiss_matches"]["total"] == 1
        assert result["swiss_matches"]["completed"] == 1
        assert result["elimination_matches"]["total"] == 1
        assert result["elimination_matches"]["scheduled"] == 1
    
    @pytest.mark.asyncio
    async def test_update_swiss_match(self, match_service, test_session, sample_teams, sample_swiss_round):
        """Test updating Swiss match."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_swiss_round)
        test_session.commit()
        
        match_data = SwissMatchCreate(
            swiss_round_id=1,
            team1_id=1,
            team2_id=2
        )
        created_match = await match_service.create_swiss_match(test_session, match_data)
        
        update_data = SwissMatchUpdate(
            winner_id=1,
            scores={"team1_score": 3, "team2_score": 1},
            status=MatchStatus.COMPLETED
        )
        
        # Act
        result = await match_service.update_swiss_match(test_session, created_match.id, update_data)
        
        # Assert
        assert result is not None
        assert result.winner_id == 1
        assert result.scores == {"team1_score": 3, "team2_score": 1}
        assert result.status == MatchStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_update_elimination_match(self, match_service, test_session, sample_teams, sample_elimination_bracket):
        """Test updating elimination match."""
        # Arrange
        for team in sample_teams:
            test_session.add(team)
        test_session.add(sample_elimination_bracket)
        test_session.commit()
        
        match_data = EliminationMatchCreate(
            bracket_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1,
            match_number=1
        )
        created_match = await match_service.create_elimination_match(test_session, match_data)
        
        update_data = EliminationMatchUpdate(
            winner_id=2,
            scores={"team1_score": 1, "team2_score": 3},
            status=MatchStatus.COMPLETED
        )
        
        # Act
        result = await match_service.update_elimination_match(test_session, created_match.id, update_data)
        
        # Assert
        assert result is not None
        assert result.winner_id == 2
        assert result.scores == {"team1_score": 1, "team2_score": 3}
        assert result.status == MatchStatus.COMPLETED
