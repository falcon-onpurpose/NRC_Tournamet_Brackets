"""
Match Service for NRC Tournament Program

Handles match creation, management, and result processing for both Swiss and elimination matches.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, and_, or_
from contextlib import contextmanager

from models import (
    SwissMatch, EliminationMatch, Team, Tournament, SwissRound, 
    EliminationBracket, MatchStatus
)
from schemas import (
    SwissMatchCreate, SwissMatchUpdate, SwissMatchResponse,
    EliminationMatchCreate, EliminationMatchUpdate, EliminationMatchResponse
)
from services.validation_service import ValidationService
from config import Settings


class MatchService:
    """Service for managing tournament matches."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.validation_service = ValidationService()
    
    @contextmanager
    def get_session(self, session: Session):
        """Context manager for database session."""
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    # Swiss Match Methods
    async def create_swiss_match(
        self, 
        session: Session, 
        match_data: SwissMatchCreate
    ) -> SwissMatchResponse:
        """Create a new Swiss match."""
        # Validate match data
        validation_result = self.validation_service.validate_match_data(match_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid match data: {validation_result.errors}")
        
        # Check if teams exist
        team1 = session.get(Team, match_data.team1_id)
        team2 = session.get(Team, match_data.team2_id)
        if not team1 or not team2:
            raise ValueError("One or both teams not found")
        
        # Create match
        match = SwissMatch(
            swiss_round_id=match_data.swiss_round_id,
            team1_id=match_data.team1_id,
            team2_id=match_data.team2_id,
            status=MatchStatus.SCHEDULED.value,
            scheduled_time=match_data.scheduled_time
        )
        
        session.add(match)
        session.commit()
        session.refresh(match)
        
        return self._create_swiss_match_response(session, match)
    
    async def get_swiss_match(
        self, 
        session: Session, 
        match_id: int
    ) -> Optional[SwissMatchResponse]:
        """Get a Swiss match by ID."""
        match = session.get(SwissMatch, match_id)
        if not match:
            return None
        
        return self._create_swiss_match_response(session, match)
    
    async def get_swiss_matches_by_round(
        self, 
        session: Session, 
        round_id: int
    ) -> List[SwissMatchResponse]:
        """Get all matches for a specific Swiss round."""
        statement = select(SwissMatch).where(SwissMatch.swiss_round_id == round_id)
        matches = session.exec(statement).all()
        
        return [self._create_swiss_match_response(session, match) for match in matches]
    
    async def update_swiss_match(
        self, 
        session: Session, 
        match_id: int, 
        update_data: SwissMatchUpdate
    ) -> Optional[SwissMatchResponse]:
        """Update a Swiss match."""
        match = session.get(SwissMatch, match_id)
        if not match:
            return None
        
        # Update fields
        if update_data.winner_id is not None:
            match.winner_id = update_data.winner_id
        if update_data.scores is not None:
            match.scores = update_data.scores
        if update_data.status is not None:
            match.status = update_data.status.value
        if update_data.start_time is not None:
            match.start_time = update_data.start_time
        if update_data.end_time is not None:
            match.end_time = update_data.end_time
        
        session.add(match)
        session.commit()
        session.refresh(match)
        
        return self._create_swiss_match_response(session, match)
    
    async def start_swiss_match(
        self, 
        session: Session, 
        match_id: int
    ) -> Optional[SwissMatchResponse]:
        """Start a Swiss match."""
        match = session.get(SwissMatch, match_id)
        if not match:
            return None
        
        if match.status != MatchStatus.SCHEDULED.value:
            raise ValueError("Match is not in scheduled status")
        
        match.status = MatchStatus.IN_PROGRESS.value
        match.start_time = datetime.utcnow()
        
        session.add(match)
        session.commit()
        session.refresh(match)
        
        return self._create_swiss_match_response(session, match)
    
    async def complete_swiss_match(
        self, 
        session: Session, 
        match_id: int, 
        winner_id: int, 
        scores: Dict[str, Any]
    ) -> Optional[SwissMatchResponse]:
        """Complete a Swiss match with results."""
        # Validate match result
        validation_result = self.validation_service.validate_match_result(winner_id, scores)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid match result: {validation_result.errors}")
        
        match = session.get(SwissMatch, match_id)
        if not match:
            return None
        
        if match.status != MatchStatus.IN_PROGRESS.value:
            raise ValueError("Match is not in progress")
        
        match.winner_id = winner_id
        match.scores = scores
        match.status = MatchStatus.COMPLETED.value
        match.end_time = datetime.utcnow()
        
        session.add(match)
        session.commit()
        session.refresh(match)
        
        return self._create_swiss_match_response(session, match)
    
    # Elimination Match Methods
    async def create_elimination_match(
        self, 
        session: Session, 
        match_data: EliminationMatchCreate
    ) -> EliminationMatchResponse:
        """Create a new elimination match."""
        # Validate match data
        validation_result = self.validation_service.validate_elimination_match_data(match_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid match data: {validation_result.errors}")
        
        # Check if teams exist
        team1 = session.get(Team, match_data.team1_id)
        team2 = session.get(Team, match_data.team2_id)
        if not team1 or not team2:
            raise ValueError("One or both teams not found")
        
        # Create match
        match = EliminationMatch(
            bracket_id=match_data.bracket_id,
            team1_id=match_data.team1_id,
            team2_id=match_data.team2_id,
            round_number=match_data.round_number,
            match_number=match_data.match_number,
            status=MatchStatus.SCHEDULED.value,
            scheduled_time=match_data.scheduled_time
        )
        
        session.add(match)
        session.commit()
        session.refresh(match)
        
        return self._create_elimination_match_response(session, match)
    
    async def get_elimination_match(
        self, 
        session: Session, 
        match_id: int
    ) -> Optional[EliminationMatchResponse]:
        """Get an elimination match by ID."""
        match = session.get(EliminationMatch, match_id)
        if not match:
            return None
        
        return self._create_elimination_match_response(session, match)
    
    async def get_elimination_matches_by_bracket(
        self, 
        session: Session, 
        bracket_id: int
    ) -> List[EliminationMatchResponse]:
        """Get all matches for a specific elimination bracket."""
        statement = select(EliminationMatch).where(EliminationMatch.bracket_id == bracket_id)
        matches = session.exec(statement).all()
        
        return [self._create_elimination_match_response(session, match) for match in matches]
    
    async def update_elimination_match(
        self, 
        session: Session, 
        match_id: int, 
        update_data: EliminationMatchUpdate
    ) -> Optional[EliminationMatchResponse]:
        """Update an elimination match."""
        match = session.get(EliminationMatch, match_id)
        if not match:
            return None
        
        # Update fields
        if update_data.winner_id is not None:
            match.winner_id = update_data.winner_id
        if update_data.scores is not None:
            match.scores = update_data.scores
        if update_data.status is not None:
            match.status = update_data.status.value
        if update_data.start_time is not None:
            match.start_time = update_data.start_time
        if update_data.end_time is not None:
            match.end_time = update_data.end_time
        
        session.add(match)
        session.commit()
        session.refresh(match)
        
        return self._create_elimination_match_response(session, match)
    
    async def start_elimination_match(
        self, 
        session: Session, 
        match_id: int
    ) -> Optional[EliminationMatchResponse]:
        """Start an elimination match."""
        match = session.get(EliminationMatch, match_id)
        if not match:
            return None
        
        if match.status != MatchStatus.SCHEDULED.value:
            raise ValueError("Match is not in scheduled status")
        
        match.status = MatchStatus.IN_PROGRESS.value
        match.start_time = datetime.utcnow()
        
        session.add(match)
        session.commit()
        session.refresh(match)
        
        return self._create_elimination_match_response(session, match)
    
    async def complete_elimination_match(
        self, 
        session: Session, 
        match_id: int, 
        winner_id: int, 
        scores: Dict[str, Any]
    ) -> Optional[EliminationMatchResponse]:
        """Complete an elimination match with results."""
        # Validate match result
        validation_result = self.validation_service.validate_match_result(winner_id, scores)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid match result: {validation_result.errors}")
        
        match = session.get(EliminationMatch, match_id)
        if not match:
            return None
        
        if match.status != MatchStatus.IN_PROGRESS.value:
            raise ValueError("Match is not in progress")
        
        match.winner_id = winner_id
        match.scores = scores
        match.status = MatchStatus.COMPLETED.value
        match.end_time = datetime.utcnow()
        
        session.add(match)
        session.commit()
        session.refresh(match)
        
        return self._create_elimination_match_response(session, match)
    
    # Utility Methods
    async def get_pending_matches(
        self, 
        session: Session, 
        tournament_id: int
    ) -> Dict[str, List]:
        """Get all pending matches for a tournament."""
        # Get pending Swiss matches
        swiss_statement = select(SwissMatch).join(SwissRound).where(
            and_(
                SwissRound.tournament_id == tournament_id,
                SwissMatch.status == MatchStatus.SCHEDULED.value
            )
        )
        pending_swiss = session.exec(swiss_statement).all()
        
        # Get pending elimination matches
        elimination_statement = select(EliminationMatch).join(EliminationBracket).where(
            and_(
                EliminationBracket.tournament_id == tournament_id,
                EliminationMatch.status == MatchStatus.SCHEDULED.value
            )
        )
        pending_elimination = session.exec(elimination_statement).all()
        
        return {
            "swiss_matches": [self._create_swiss_match_response(session, match) for match in pending_swiss],
            "elimination_matches": [self._create_elimination_match_response(session, match) for match in pending_elimination]
        }
    
    async def get_match_statistics(
        self, 
        session: Session, 
        tournament_id: int
    ) -> Dict[str, Any]:
        """Get match statistics for a tournament."""
        # Swiss match stats
        swiss_statement = select(SwissMatch).join(SwissRound).where(
            SwissRound.tournament_id == tournament_id
        )
        swiss_matches = session.exec(swiss_statement).all()
        
        # Elimination match stats
        elimination_statement = select(EliminationMatch).join(EliminationBracket).where(
            EliminationBracket.tournament_id == tournament_id
        )
        elimination_matches = session.exec(elimination_statement).all()
        
        return {
            "swiss_matches": {
                "total": len(swiss_matches),
                "scheduled": len([m for m in swiss_matches if m.status == MatchStatus.SCHEDULED.value]),
                "in_progress": len([m for m in swiss_matches if m.status == MatchStatus.IN_PROGRESS.value]),
                "completed": len([m for m in swiss_matches if m.status == MatchStatus.COMPLETED.value])
            },
            "elimination_matches": {
                "total": len(elimination_matches),
                "scheduled": len([m for m in elimination_matches if m.status == MatchStatus.SCHEDULED.value]),
                "in_progress": len([m for m in elimination_matches if m.status == MatchStatus.IN_PROGRESS.value]),
                "completed": len([m for m in elimination_matches if m.status == MatchStatus.COMPLETED.value])
            }
        }
    
    # Helper Methods
    def _create_swiss_match_response(
        self, 
        session: Session, 
        match: SwissMatch
    ) -> SwissMatchResponse:
        """Create a Swiss match response with team names."""
        team1 = session.get(Team, match.team1_id)
        team2 = session.get(Team, match.team2_id)
        winner = session.get(Team, match.winner_id) if match.winner_id else None
        
        return SwissMatchResponse(
            id=match.id,
            swiss_round_id=match.swiss_round_id,
            team1_id=match.team1_id,
            team2_id=match.team2_id,
            winner_id=match.winner_id,
            scores=match.scores,
            status=MatchStatus(match.status),
            start_time=match.start_time,
            end_time=match.end_time,
            created_at=match.created_at,
            team1_name=team1.name if team1 else "Unknown Team",
            team2_name=team2.name if team2 else "Unknown Team",
            winner_name=winner.name if winner else None
        )
    
    def _create_elimination_match_response(
        self, 
        session: Session, 
        match: EliminationMatch
    ) -> EliminationMatchResponse:
        """Create an elimination match response with team names."""
        team1 = session.get(Team, match.team1_id)
        team2 = session.get(Team, match.team2_id)
        winner = session.get(Team, match.winner_id) if match.winner_id else None
        
        return EliminationMatchResponse(
            id=match.id,
            bracket_id=match.bracket_id,
            team1_id=match.team1_id,
            team2_id=match.team2_id,
            winner_id=match.winner_id,
            scores=match.scores,
            status=MatchStatus(match.status),
            start_time=match.start_time,
            end_time=match.end_time,
            round_number=match.round_number,
            match_number=match.match_number,
            created_at=match.created_at,
            team1_name=team1.name if team1 else "Unknown Team",
            team2_name=team2.name if team2 else "Unknown Team",
            winner_name=winner.name if winner else None
        )
