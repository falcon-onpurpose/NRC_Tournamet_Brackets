"""
Unit tests for tournament service.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession

from services.tournament_service import TournamentService
from services.validation_service import ValidationService
from models import Tournament, Team, SwissMatch, EliminationMatch
from schemas import TournamentCreate, TournamentUpdate


class TestTournamentService:
    """Test tournament service functionality."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock()
        settings.MAX_TEAMS_PER_TOURNAMENT = 64
        settings.MAX_SWISS_ROUNDS = 10
        return settings
    
    @pytest.fixture
    def tournament_service(self, mock_settings):
        """Create tournament service instance."""
        return TournamentService(mock_settings)
    
    @pytest.mark.asyncio
    async def test_create_tournament_success(self, tournament_service, test_session: AsyncSession):
        """Test successful tournament creation."""
        # Arrange
        data = TournamentCreate(
            name="Test Tournament",
            format="hybrid_swiss_elimination",
            location="Test Arena",
            description="Test tournament",
            swiss_rounds_count=3,
            start_date=datetime.utcnow() + timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=2)
        )
        
        # Act
        result = await tournament_service.create_tournament(data, test_session)
        
        # Assert
        assert result.name == "Test Tournament"
        assert result.format == "hybrid_swiss_elimination"
        assert result.status == "setup"
        assert result.id is not None
        assert result.swiss_rounds_count == 3
    
    @pytest.mark.asyncio
    async def test_create_tournament_validation_failure(self, tournament_service, test_session: AsyncSession):
        """Test tournament creation with invalid data."""
        # Arrange
        data = TournamentCreate(
            name="",  # Invalid: empty name
            format="invalid_format",  # Invalid: unknown format
            location="Test Arena",
            description="Test tournament",
            swiss_rounds_count=0,  # Invalid: zero rounds
            start_date=datetime.utcnow() + timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=2)
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid tournament data"):
            await tournament_service.create_tournament(data, test_session)
    
    @pytest.mark.asyncio
    async def test_get_tournament_success(self, tournament_service, test_session: AsyncSession, sample_tournament):
        """Test successful tournament retrieval."""
        # Act
        result = await tournament_service.get_tournament(sample_tournament.id, test_session)
        
        # Assert
        assert result.id == sample_tournament.id
        assert result.name == sample_tournament.name
    
    @pytest.mark.asyncio
    async def test_get_tournament_not_found(self, tournament_service, test_session: AsyncSession):
        """Test tournament retrieval when not found."""
        # Act & Assert
        with pytest.raises(ValueError, match="Tournament with ID 999 not found"):
            await tournament_service.get_tournament(999, test_session)
    
    @pytest.mark.asyncio
    async def test_get_tournaments_with_filters(self, tournament_service, test_session: AsyncSession, sample_tournament):
        """Test retrieving tournaments with filters."""
        # Act
        result = await tournament_service.get_tournaments({"status": "setup"}, test_session)
        
        # Assert
        assert len(result) > 0
        assert all(t.status == "setup" for t in result)
    
    @pytest.mark.asyncio
    async def test_update_tournament_success(self, tournament_service, test_session: AsyncSession, sample_tournament):
        """Test successful tournament update."""
        # Arrange
        data = TournamentUpdate(name="Updated Tournament")
        
        # Act
        result = await tournament_service.update_tournament(sample_tournament.id, data, test_session)
        
        # Assert
        assert result.name == "Updated Tournament"
        assert result.id == sample_tournament.id
    
    @pytest.mark.asyncio
    async def test_delete_tournament_success(self, tournament_service, test_session: AsyncSession, sample_tournament):
        """Test successful tournament deletion."""
        # Act
        result = await tournament_service.delete_tournament(sample_tournament.id, test_session)
        
        # Assert
        assert result is True
        
        # Verify tournament is deleted
        with pytest.raises(ValueError, match="Tournament with ID"):
            await tournament_service.get_tournament(sample_tournament.id, test_session)
    
    @pytest.mark.asyncio
    async def test_delete_active_tournament_failure(self, tournament_service, test_session: AsyncSession):
        """Test tournament deletion when tournament is active."""
        # Arrange
        tournament = Tournament(
            name="Active Tournament",
            format="hybrid_swiss_elimination",
            status="active",
            location="Test Arena",
            swiss_rounds=3
        )
        test_session.add(tournament)
        await test_session.commit()
        await test_session.refresh(tournament)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot delete tournament"):
            await tournament_service.delete_tournament(tournament.id, test_session)
    
    @pytest.mark.asyncio
    async def test_start_tournament_success(self, tournament_service, test_session: AsyncSession, sample_tournament, sample_teams):
        """Test successful tournament start."""
        # Act
        result = await tournament_service.start_tournament(sample_tournament.id, test_session)
        
        # Assert
        assert result.status == "active"
        assert result.id == sample_tournament.id
    
    @pytest.mark.asyncio
    async def test_start_tournament_no_teams_failure(self, tournament_service, test_session: AsyncSession):
        """Test tournament start when no teams are registered."""
        # Arrange
        tournament = Tournament(
            name="No Teams Tournament",
            format="hybrid_swiss_elimination",
            status="setup",
            location="Test Arena",
            swiss_rounds=3
        )
        test_session.add(tournament)
        await test_session.commit()
        await test_session.refresh(tournament)
        
        # Act & Assert
        with pytest.raises(ValueError, match="no teams registered"):
            await tournament_service.start_tournament(tournament.id, test_session)
    
    @pytest.mark.asyncio
    async def test_start_tournament_wrong_status_failure(self, tournament_service, test_session: AsyncSession, sample_tournament):
        """Test tournament start when status is not setup."""
        # Arrange - Update tournament to active status
        sample_tournament.status = "active"
        test_session.add(sample_tournament)
        await test_session.commit()
        
        # Act & Assert
        with pytest.raises(ValueError, match="cannot be started"):
            await tournament_service.start_tournament(sample_tournament.id, test_session)
    
    @pytest.mark.asyncio
    async def test_pause_tournament_success(self, tournament_service, test_session: AsyncSession, sample_tournament):
        """Test successful tournament pause."""
        # Arrange - Start tournament first
        sample_tournament.status = "active"
        test_session.add(sample_tournament)
        await test_session.commit()
        
        # Act
        result = await tournament_service.pause_tournament(sample_tournament.id, test_session)
        
        # Assert
        assert result.status == "paused"
    
    @pytest.mark.asyncio
    async def test_resume_tournament_success(self, tournament_service, test_session: AsyncSession, sample_tournament):
        """Test successful tournament resume."""
        # Arrange - Pause tournament first
        sample_tournament.status = "paused"
        test_session.add(sample_tournament)
        await test_session.commit()
        
        # Act
        result = await tournament_service.resume_tournament(sample_tournament.id, test_session)
        
        # Assert
        assert result.status == "active"
    
    @pytest.mark.asyncio
    async def test_complete_tournament_success(self, tournament_service, test_session: AsyncSession, sample_tournament):
        """Test successful tournament completion."""
        # Arrange - Set tournament to active
        sample_tournament.status = "active"
        test_session.add(sample_tournament)
        await test_session.commit()
        
        # Act
        result = await tournament_service.complete_tournament(sample_tournament.id, test_session)
        
        # Assert
        assert result.status == "completed"
        assert result.end_date is not None
    
    @pytest.mark.asyncio
    async def test_get_tournament_stats(self, tournament_service, test_session: AsyncSession, sample_tournament, sample_teams, sample_matches):
        """Test tournament statistics calculation."""
        # Act
        stats = await tournament_service.get_tournament_stats(sample_tournament.id, test_session)
        
        # Assert
        assert stats["tournament_id"] == sample_tournament.id
        assert stats["tournament_name"] == sample_tournament.name
        assert stats["status"] == sample_tournament.status
        assert stats["team_count"] == 4  # sample_teams has 4 teams
        assert stats["total_matches"] == 2  # sample_matches has 2 matches
        assert stats["completed_matches"] == 0  # no completed matches
        assert stats["progress_percentage"] == 0.0
    
    @pytest.mark.asyncio
    async def test_get_tournament_stats_with_completed_matches(self, tournament_service, test_session: AsyncSession, sample_tournament, sample_teams, sample_matches):
        """Test tournament statistics with completed matches."""
        # Arrange - Complete one match
        sample_matches[0].status = "completed"
        sample_matches[0].winner_id = sample_matches[0].team1_id
        sample_matches[0].scores = {"team1_score": 3, "team2_score": 1}
        test_session.add_all(sample_matches)
        await test_session.commit()
        
        # Act
        stats = await tournament_service.get_tournament_stats(sample_tournament.id, test_session)
        
        # Assert
        assert stats["completed_matches"] == 1
        assert stats["progress_percentage"] == 50.0  # 1 out of 2 matches completed


class TestTournamentServiceIntegration:
    """Integration tests for tournament service with database."""
    
    @pytest.mark.asyncio
    async def test_tournament_lifecycle(self, test_session: AsyncSession, sample_teams):
        """Test complete tournament lifecycle."""
        # Arrange
        from config import get_settings
        settings = get_settings()
        service = TournamentService(settings, test_session)
        
        # Create tournament
        data = TournamentCreate(
            name="Lifecycle Test Tournament",
            format="hybrid_swiss_elimination",
            location="Test Arena",
            description="Test tournament lifecycle",
            swiss_rounds=3,
            start_date=datetime.utcnow() + timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=2)
        )
        
        tournament = await service.create_tournament(data, test_session)
        
        # Start tournament
        started_tournament = await service.start_tournament(tournament.id, test_session)
        assert started_tournament.status == "active"
        
        # Pause tournament
        paused_tournament = await service.pause_tournament(tournament.id, test_session)
        assert paused_tournament.status == "paused"
        
        # Resume tournament
        resumed_tournament = await service.resume_tournament(tournament.id, test_session)
        assert resumed_tournament.status == "active"
        
        # Complete tournament
        completed_tournament = await service.complete_tournament(tournament.id, test_session)
        assert completed_tournament.status == "completed"
        
        # Get stats
        stats = await service.get_tournament_stats(tournament.id, test_session)
        assert stats["status"] == "completed"
        assert stats["team_count"] == 4  # sample_teams has 4 teams
