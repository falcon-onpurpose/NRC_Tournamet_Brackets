"""
Match service for business logic operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain.shared.repository import BaseService
from domain.match.match_repository import MatchRepository
from domain.match.match_validator import MatchValidator
from models import SwissMatch, EliminationMatch, Team, Tournament
from schemas import (
    SwissMatchResponse, EliminationMatchResponse, MatchResultCreate,
    SwissMatchCreate, EliminationMatchCreate, MatchStatisticsResponse
)


class MatchService(BaseService):
    """Service for match-related business logic."""
    
    def __init__(self, repository: MatchRepository, validator: MatchValidator):
        super().__init__(repository)
        self.validator = validator
    
    # Swiss Match Methods
    async def create_swiss_match(self, match_data: SwissMatchCreate) -> SwissMatchResponse:
        """Create a new Swiss match."""
        # Validate match data
        validation_result = self.validator.validate_swiss_match_data(
            match_data.tournament_id,
            match_data.team1_id,
            match_data.team2_id,
            match_data.round_number
        )
        if not validation_result.is_valid:
            raise ValueError(f"Invalid Swiss match data: {validation_result.errors}")
        
        # Validate team participation
        participation_result = self.validator.validate_team_participation(
            match_data.team1_id,
            match_data.team2_id,
            match_data.tournament_id
        )
        if not participation_result.is_valid:
            raise ValueError(f"Team participation validation failed: {participation_result.errors}")
        
        # Create Swiss match
        match = SwissMatch(
            tournament_id=match_data.tournament_id,
            team1_id=match_data.team1_id,
            team2_id=match_data.team2_id,
            round_number=match_data.round_number,
            status="pending"
        )
        
        saved_match = await self.repository.save_swiss_match(match)
        return SwissMatchResponse.model_validate(saved_match)
    
    async def get_swiss_matches(self, **filters) -> List[SwissMatchResponse]:
        """Get Swiss matches with optional filters."""
        matches = await self.repository.find_all_swiss_matches(**filters)
        return [SwissMatchResponse.model_validate(match) for match in matches]
    
    async def get_swiss_match(self, match_id: int) -> Optional[SwissMatchResponse]:
        """Get Swiss match by ID."""
        match = await self.repository.find_swiss_match_by_id(match_id)
        if not match:
            return None
        
        return SwissMatchResponse.model_validate(match)
    
    async def complete_swiss_match(self, match_id: int, result_data: MatchResultCreate) -> Optional[SwissMatchResponse]:
        """Complete a Swiss match with results."""
        # Validate match exists
        validation_result = self.validator.validate_match_exists(match_id)
        if not validation_result.is_valid:
            raise ValueError(f"Match validation failed: {validation_result.errors}")
        
        match = await self.repository.find_swiss_match_by_id(match_id)
        if not match:
            return None
        
        # Validate result data
        result_validation = self.validator.validate_match_result(result_data)
        if not result_validation.is_valid:
            raise ValueError(f"Invalid result data: {result_validation.errors}")
        
        # Update match with results
        match.winner_id = result_data.winner_id
        match.team1_score = result_data.team1_score
        match.team2_score = result_data.team2_score
        match.status = "completed"
        match.completed_at = datetime.now()
        
        saved_match = await self.repository.save_swiss_match(match)
        return SwissMatchResponse.model_validate(saved_match)
    
    # Elimination Match Methods
    async def create_elimination_match(self, match_data: EliminationMatchCreate) -> EliminationMatchResponse:
        """Create a new elimination match."""
        # Validate match data
        validation_result = self.validator.validate_elimination_match_data(
            match_data.tournament_id,
            match_data.team1_id,
            match_data.team2_id,
            match_data.bracket_id,
            match_data.round_number
        )
        if not validation_result.is_valid:
            raise ValueError(f"Invalid elimination match data: {validation_result.errors}")
        
        # Validate team participation
        participation_result = self.validator.validate_team_participation(
            match_data.team1_id,
            match_data.team2_id,
            match_data.tournament_id
        )
        if not participation_result.is_valid:
            raise ValueError(f"Team participation validation failed: {participation_result.errors}")
        
        # Create elimination match
        match = EliminationMatch(
            tournament_id=match_data.tournament_id,
            bracket_id=match_data.bracket_id,
            team1_id=match_data.team1_id,
            team2_id=match_data.team2_id,
            round_number=match_data.round_number,
            status="pending"
        )
        
        saved_match = await self.repository.save_elimination_match(match)
        return EliminationMatchResponse.model_validate(saved_match)
    
    async def get_elimination_matches(self, **filters) -> List[EliminationMatchResponse]:
        """Get elimination matches with optional filters."""
        matches = await self.repository.find_all_elimination_matches(**filters)
        return [EliminationMatchResponse.model_validate(match) for match in matches]
    
    async def get_elimination_match(self, match_id: int) -> Optional[EliminationMatchResponse]:
        """Get elimination match by ID."""
        match = await self.repository.find_elimination_match_by_id(match_id)
        if not match:
            return None
        
        return EliminationMatchResponse.model_validate(match)
    
    async def update_elimination_match(self, match_id: int, match_data: EliminationMatchCreate) -> Optional[EliminationMatchResponse]:
        """Update an elimination match."""
        # Validate match exists
        validation_result = self.validator.validate_match_exists(match_id)
        if not validation_result.is_valid:
            raise ValueError(f"Match validation failed: {validation_result.errors}")
        
        match = await self.repository.find_elimination_match_by_id(match_id)
        if not match:
            return None
        
        # Validate match data
        data_validation = self.validator.validate_elimination_match_data(
            match_data.tournament_id,
            match_data.team1_id,
            match_data.team2_id,
            match_data.bracket_id,
            match_data.round_number
        )
        if not data_validation.is_valid:
            raise ValueError(f"Invalid match data: {data_validation.errors}")
        
        # Update match fields
        match.tournament_id = match_data.tournament_id
        match.bracket_id = match_data.bracket_id
        match.team1_id = match_data.team1_id
        match.team2_id = match_data.team2_id
        match.round_number = match_data.round_number
        
        saved_match = await self.repository.save_elimination_match(match)
        return EliminationMatchResponse.model_validate(saved_match)
    
    async def start_elimination_match(self, match_id: int) -> Optional[EliminationMatchResponse]:
        """Start an elimination match."""
        # Validate match exists
        validation_result = self.validator.validate_match_exists(match_id)
        if not validation_result.is_valid:
            raise ValueError(f"Match validation failed: {validation_result.errors}")
        
        match = await self.repository.find_elimination_match_by_id(match_id)
        if not match:
            return None
        
        # Validate status transition
        status_validation = self.validator.validate_match_status(match.status, "in_progress")
        if not status_validation.is_valid:
            raise ValueError(f"Status transition failed: {status_validation.errors}")
        
        # Update match status
        match.status = "in_progress"
        match.started_at = datetime.now()
        
        saved_match = await self.repository.save_elimination_match(match)
        return EliminationMatchResponse.model_validate(saved_match)
    
    async def complete_elimination_match(self, match_id: int, result_data: MatchResultCreate) -> Optional[EliminationMatchResponse]:
        """Complete an elimination match with results."""
        # Validate match exists
        validation_result = self.validator.validate_match_exists(match_id)
        if not validation_result.is_valid:
            raise ValueError(f"Match validation failed: {validation_result.errors}")
        
        match = await self.repository.find_elimination_match_by_id(match_id)
        if not match:
            return None
        
        # Validate result data
        result_validation = self.validator.validate_match_result(result_data)
        if not result_validation.is_valid:
            raise ValueError(f"Invalid result data: {result_validation.errors}")
        
        # Update match with results
        match.winner_id = result_data.winner_id
        match.team1_score = result_data.team1_score
        match.team2_score = result_data.team2_score
        match.status = "completed"
        match.completed_at = datetime.now()
        
        saved_match = await self.repository.save_elimination_match(match)
        return EliminationMatchResponse.model_validate(saved_match)
    
    # General Match Methods
    async def get_pending_matches(self, tournament_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get pending matches for a tournament."""
        return await self.repository.find_pending_matches(tournament_id)
    
    async def get_match_statistics(self, tournament_id: Optional[int] = None) -> MatchStatisticsResponse:
        """Get match statistics."""
        stats = await self.repository.get_match_statistics(tournament_id)
        return MatchStatisticsResponse(**stats)
    
    async def delete_match(self, match_id: int) -> bool:
        """Delete a match (Swiss or elimination)."""
        # Validate match exists
        validation_result = self.validator.validate_match_exists(match_id)
        if not validation_result.is_valid:
            raise ValueError(f"Match validation failed: {validation_result.errors}")
        
        return await self.repository.delete(match_id)
