"""
Unit tests for tournament core functionality.
"""
import pytest
from unittest.mock import AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession

from models import Tournament, Team, SwissMatch, EliminationMatch
from schemas import TournamentCreate, TournamentUpdate, SwissMatchCreate


class TestTournamentService:
    """Test tournament service functionality."""
    
    @pytest.mark.asyncio
    async def test_create_tournament_success(self, test_session: AsyncSession):
        """Test successful tournament creation."""
        # Arrange
        from services.tournament_service import TournamentService
        service = TournamentService(test_session)
        data = TournamentCreate(
            name="Test Tournament",
            format="hybrid_swiss_elimination",
            location="Test Arena",
            description="Test tournament",
            swiss_rounds_count=3
        )
        
        # Act
        result = await service.create_tournament(data)
        
        # Assert
        assert result.name == "Test Tournament"
        assert result.format == "hybrid_swiss_elimination"
        assert result.status == "setup"
        assert result.id is not None
        assert result.swiss_rounds_count == 3
    
    @pytest.mark.asyncio
    async def test_get_tournament_success(self, test_session: AsyncSession, sample_tournament):
        """Test successful tournament retrieval."""
        # Arrange
        from services.tournament_service import TournamentService
        service = TournamentService(test_session)
        
        # Act
        result = await service.get_tournament(sample_tournament.id)
        
        # Assert
        assert result.id == sample_tournament.id
        assert result.name == sample_tournament.name
    
    @pytest.mark.asyncio
    async def test_get_tournament_not_found(self, test_session: AsyncSession):
        """Test tournament retrieval when not found."""
        # Arrange
        from services.tournament_service import TournamentService
        service = TournamentService(test_session)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Tournament not found"):
            await service.get_tournament(999)
    
    @pytest.mark.asyncio
    async def test_update_tournament_success(self, test_session: AsyncSession, sample_tournament):
        """Test successful tournament update."""
        # Arrange
        from services.tournament_service import TournamentService
        service = TournamentService(test_session)
        data = TournamentUpdate(name="Updated Tournament")
        
        # Act
        result = await service.update_tournament(sample_tournament.id, data)
        
        # Assert
        assert result.name == "Updated Tournament"
        assert result.id == sample_tournament.id
    
    @pytest.mark.asyncio
    async def test_delete_tournament_success(self, test_session: AsyncSession, sample_tournament):
        """Test successful tournament deletion."""
        # Arrange
        from services.tournament_service import TournamentService
        service = TournamentService(test_session)
        
        # Act
        result = await service.delete_tournament(sample_tournament.id)
        
        # Assert
        assert result is True
        
        # Verify tournament is deleted
        with pytest.raises(ValueError, match="Tournament not found"):
            await service.get_tournament(sample_tournament.id)


class TestMatchService:
    """Test match service functionality."""
    
    @pytest.mark.asyncio
    async def test_create_swiss_match_success(self, test_session: AsyncSession, sample_tournament, sample_teams):
        """Test successful Swiss match creation."""
        # Arrange
        from services.match_service import MatchService
        service = MatchService(test_session)
        data = SwissMatchCreate(
            tournament_id=sample_tournament.id,
            team1_id=sample_teams[0].id,
            team2_id=sample_teams[1].id,
            round_number=1
        )
        
        # Act
        result = await service.create_swiss_match(data)
        
        # Assert
        assert result.tournament_id == sample_tournament.id
        assert result.team1_id == sample_teams[0].id
        assert result.team2_id == sample_teams[1].id
        assert result.round_number == 1
        assert result.status == "scheduled"
    
    @pytest.mark.asyncio
    async def test_get_upcoming_matches(self, test_session: AsyncSession, sample_tournament, sample_matches):
        """Test retrieving upcoming matches."""
        # Arrange
        from services.match_service import MatchService
        service = MatchService(test_session)
        
        # Act
        result = await service.get_upcoming_matches(sample_tournament.id)
        
        # Assert
        assert len(result) == 2
        assert all(match.tournament_id == sample_tournament.id for match in result)
        assert all(match.status == "scheduled" for match in result)
    
    @pytest.mark.asyncio
    async def test_update_match_result_success(self, test_session: AsyncSession, sample_matches):
        """Test successful match result update."""
        # Arrange
        from services.match_service import MatchService
        service = MatchService(test_session)
        match = sample_matches[0]
        winner_id = match.team1_id
        scores = {"team1_score": 3, "team2_score": 1}
        
        # Act
        result = await service.update_match_result(match.id, winner_id, scores)
        
        # Assert
        assert result.winner_id == winner_id
        assert result.scores == scores
        assert result.status == "completed"


class TestBracketGeneration:
    """Test bracket generation algorithms."""
    
    @pytest.mark.asyncio
    async def test_generate_swiss_brackets_even_teams(self, test_session: AsyncSession, sample_tournament, sample_teams):
        """Test Swiss bracket generation with even number of teams."""
        # Arrange
        from services.bracket_service import BracketService
        service = BracketService(test_session)
        
        # Act
        matches = await service.generate_swiss_brackets(sample_tournament.id, 1)
        
        # Assert
        assert len(matches) == 2  # 4 teams = 2 matches
        assert all(match.round_number == 1 for match in matches)
        assert all(match.status == "scheduled" for match in matches)
        
        # Verify no team plays twice
        team_ids = []
        for match in matches:
            team_ids.extend([match.team1_id, match.team2_id])
        assert len(team_ids) == len(set(team_ids))
    
    @pytest.mark.asyncio
    async def test_generate_swiss_brackets_odd_teams(self, test_session: AsyncSession, sample_tournament):
        """Test Swiss bracket generation with odd number of teams."""
        # Arrange
        from services.bracket_service import BracketService
        service = BracketService(test_session)
        
        # Create 5 teams (odd number)
        teams = await create_test_teams(test_session, sample_tournament.id, 5)
        
        # Act
        matches = await service.generate_swiss_brackets(sample_tournament.id, 1)
        
        # Assert
        assert len(matches) == 2  # 5 teams = 2 matches + 1 bye
        assert all(match.round_number == 1 for match in matches)
        
        # Verify one team gets a bye
        team_ids = []
        for match in matches:
            team_ids.extend([match.team1_id, match.team2_id])
        assert len(set(team_ids)) == 4  # 4 teams play, 1 gets bye
    
    @pytest.mark.asyncio
    async def test_generate_elimination_brackets(self, test_session: AsyncSession, sample_tournament, sample_teams):
        """Test elimination bracket generation."""
        # Arrange
        from services.bracket_service import BracketService
        service = BracketService(test_session)
        
        # Act
        brackets = await service.generate_elimination_brackets(sample_tournament.id, "winners")
        
        # Assert
        assert len(brackets) == 1  # 4 teams = 1 bracket
        assert brackets[0].bracket_type == "winners"
        assert brackets[0].status == "active"
        
        # Verify matches are created
        matches = await service.get_bracket_matches(brackets[0].id)
        assert len(matches) == 2  # 4 teams = 2 matches in first round


class TestStandingsCalculation:
    """Test standings calculation functionality."""
    
    @pytest.mark.asyncio
    async def test_calculate_swiss_standings(self, test_session: AsyncSession, sample_tournament, sample_teams, sample_matches):
        """Test Swiss standings calculation."""
        # Arrange
        from services.standings_service import StandingsService
        service = StandingsService(test_session)
        
        # Complete some matches
        match1 = sample_matches[0]
        match1.winner_id = match1.team1_id
        match1.scores = {"team1_score": 3, "team2_score": 1}
        match1.status = "completed"
        
        match2 = sample_matches[1]
        match2.winner_id = match2.team2_id
        match2.scores = {"team1_score": 1, "team2_score": 3}
        match2.status = "completed"
        
        test_session.add_all([match1, match2])
        await test_session.commit()
        
        # Act
        standings = await service.calculate_swiss_standings(sample_tournament.id)
        
        # Assert
        assert len(standings) == 4
        
        # Find teams with wins
        winning_teams = [s for s in standings if s.wins > 0]
        assert len(winning_teams) == 2
        
        # Verify standings are sorted by wins
        assert standings[0].wins >= standings[1].wins
        assert standings[1].wins >= standings[2].wins
    
    @pytest.mark.asyncio
    async def test_calculate_elimination_standings(self, test_session: AsyncSession, sample_tournament, sample_teams):
        """Test elimination standings calculation."""
        # Arrange
        from services.standings_service import StandingsService
        service = StandingsService(test_session)
        
        # Create elimination bracket and matches
        from services.bracket_service import BracketService
        bracket_service = BracketService(test_session)
        brackets = await bracket_service.generate_elimination_brackets(sample_tournament.id, "winners")
        
        # Complete some matches
        matches = await bracket_service.get_bracket_matches(brackets[0].id)
        for i, match in enumerate(matches):
            match.winner_id = match.team1_id if i % 2 == 0 else match.team2_id
            match.scores = {"team1_score": 3, "team2_score": 1}
            match.status = "completed"
        
        test_session.add_all(matches)
        await test_session.commit()
        
        # Act
        standings = await service.calculate_elimination_standings(sample_tournament.id)
        
        # Assert
        assert len(standings) == 4
        assert any(s.eliminated for s in standings)
        assert any(not s.eliminated for s in standings)


class TestValidation:
    """Test validation functionality."""
    
    @pytest.mark.asyncio
    async def test_validate_tournament_data_success(self):
        """Test successful tournament data validation."""
        # Arrange
        from services.validation_service import ValidationService
        service = ValidationService()
        data = TournamentCreate(
            name="Valid Tournament",
            format="hybrid_swiss_elimination",
            location="Valid Arena",
            description="Valid description",
            swiss_rounds=3
        )
        
        # Act
        result = service.validate_tournament_data(data)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_tournament_data_invalid(self):
        """Test tournament data validation with invalid data."""
        # Arrange
        from services.validation_service import ValidationService
        service = ValidationService()
        data = TournamentCreate(
            name="",  # Invalid: empty name
            format="invalid_format",  # Invalid: unknown format
            location="Valid Arena",
            description="Valid description",
            swiss_rounds=0  # Invalid: zero rounds
        )
        
        # Act
        result = service.validate_tournament_data(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("name" in error.lower() for error in result.errors)
        assert any("format" in error.lower() for error in result.errors)
        assert any("rounds" in error.lower() for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_validate_match_data_success(self):
        """Test successful match data validation."""
        # Arrange
        from services.validation_service import ValidationService
        service = ValidationService()
        data = SwissMatchCreate(
            tournament_id=1,
            team1_id=1,
            team2_id=2,
            round_number=1
        )
        
        # Act
        result = service.validate_match_data(data)
        
        # Assert
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_match_data_same_team(self):
        """Test match data validation with same team."""
        # Arrange
        from services.validation_service import ValidationService
        service = ValidationService()
        data = SwissMatchCreate(
            tournament_id=1,
            team1_id=1,
            team2_id=1,  # Same as team1_id
            round_number=1
        )
        
        # Act
        result = service.validate_match_data(data)
        
        # Assert
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("same team" in error.lower() for error in result.errors)
