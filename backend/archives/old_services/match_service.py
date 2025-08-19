"""
Match Service for NRC Tournament Program

Handles match creation, management, and result processing for both Swiss and elimination matches.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from models import (
    SwissMatch, EliminationMatch, Team, Tournament, SwissRound, 
    EliminationBracket, MatchStatus
)
from schemas import (
    SwissMatchCreate, SwissMatchUpdate, SwissMatchResponse,
    EliminationMatchCreate, EliminationMatchUpdate, EliminationMatchResponse,
    MatchResultCreate
)
from services.validation_service import ValidationService
from config import Settings


class MatchService:
    """Service for managing tournament matches."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.validation_service = ValidationService()
    
    # Swiss Match Methods
    async def create_swiss_match(
        self, 
        session: AsyncSession, 
        match_data: SwissMatchCreate
    ) -> SwissMatchResponse:
        """Create a new Swiss match."""
        # Validate match data
        validation_result = self.validation_service.validate_match_data(match_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid match data: {validation_result.errors}")
        
        # Check if teams exist
        team1_result = await session.execute(
            select(Team).where(Team.id == match_data.team1_id)
        )
        team1 = team1_result.scalar_one_or_none()
        
        team2_result = await session.execute(
            select(Team).where(Team.id == match_data.team2_id)
        )
        team2 = team2_result.scalar_one_or_none()
        
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
        await session.commit()
        await session.refresh(match)
        
        return await self._create_swiss_match_response(session, match)
    
    async def get_swiss_matches(
        self,
        session: AsyncSession,
        tournament_id: Optional[int] = None,
        round_number: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[SwissMatchResponse]:
        """Get Swiss matches with optional filters."""
        stmt = select(SwissMatch).join(SwissRound)
        
        if tournament_id:
            stmt = stmt.where(SwissRound.tournament_id == tournament_id)
        if round_number:
            stmt = stmt.where(SwissRound.round_number == round_number)
        if status_filter:
            stmt = stmt.where(SwissMatch.status == status_filter)
        
        result = await session.execute(stmt)
        matches = result.scalars().all()
        
        return [await self._create_swiss_match_response(session, match) for match in matches]
    
    async def get_swiss_match(
        self, 
        session: AsyncSession, 
        match_id: int
    ) -> Optional[SwissMatchResponse]:
        """Get a Swiss match by ID."""
        result = await session.execute(
            select(SwissMatch).where(SwissMatch.id == match_id)
        )
        match = result.scalar_one_or_none()
        if not match:
            return None
        
        return await self._create_swiss_match_response(session, match)
    
    async def get_swiss_matches_by_round(
        self, 
        session: AsyncSession, 
        round_id: int
    ) -> List[SwissMatchResponse]:
        """Get all matches for a specific Swiss round."""
        result = await session.execute(
            select(SwissMatch).where(SwissMatch.swiss_round_id == round_id)
        )
        matches = result.scalars().all()
        
        return [await self._create_swiss_match_response(session, match) for match in matches]
    
    async def update_swiss_match(
        self, 
        session: AsyncSession, 
        match_id: int, 
        update_data: SwissMatchUpdate
    ) -> Optional[SwissMatchResponse]:
        """Update a Swiss match."""
        result = await session.execute(
            select(SwissMatch).where(SwissMatch.id == match_id)
        )
        match = result.scalar_one_or_none()
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
        await session.commit()
        await session.refresh(match)
        
        return await self._create_swiss_match_response(session, match)
    
    async def start_swiss_match(
        self, 
        session: AsyncSession, 
        match_id: int
    ) -> Optional[SwissMatchResponse]:
        """Start a Swiss match."""
        result = await session.execute(
            select(SwissMatch).where(SwissMatch.id == match_id)
        )
        match = result.scalar_one_or_none()
        if not match:
            return None
        
        if match.status != MatchStatus.SCHEDULED.value:
            raise ValueError("Match is not in scheduled status")
        
        match.status = MatchStatus.IN_PROGRESS.value
        match.start_time = datetime.utcnow()
        
        session.add(match)
        await session.commit()
        await session.refresh(match)
        
        return await self._create_swiss_match_response(session, match)
    
    async def complete_swiss_match(
        self, 
        session: AsyncSession, 
        match_id: int, 
        result_data: MatchResultCreate
    ) -> Optional[SwissMatchResponse]:
        """Complete a Swiss match with results."""
        # Validate match result
        validation_result = self.validation_service.validate_match_result(
            result_data.winner_id, 
            {"team1_score": result_data.team1_score, "team2_score": result_data.team2_score}
        )
        if not validation_result.is_valid:
            raise ValueError(f"Invalid match result: {validation_result.errors}")
        
        result = await session.execute(
            select(SwissMatch).where(SwissMatch.id == match_id)
        )
        match = result.scalar_one_or_none()
        if not match:
            return None
        
        if match.status != MatchStatus.IN_PROGRESS.value:
            raise ValueError("Match is not in progress")
        
        match.winner_id = result_data.winner_id
        match.scores = {"team1_score": result_data.team1_score, "team2_score": result_data.team2_score}
        match.status = MatchStatus.COMPLETED.value
        match.end_time = datetime.utcnow()
        
        session.add(match)
        await session.commit()
        await session.refresh(match)
        
        return await self._create_swiss_match_response(session, match)
    
    # Elimination Match Methods
    async def create_elimination_match(
        self, 
        session: AsyncSession, 
        match_data: EliminationMatchCreate
    ) -> EliminationMatchResponse:
        """Create a new elimination match."""
        # Validate match data
        validation_result = self.validation_service.validate_elimination_match_data(match_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid match data: {validation_result.errors}")
        
        # Check if teams exist
        team1_result = await session.execute(
            select(Team).where(Team.id == match_data.team1_id)
        )
        team1 = team1_result.scalar_one_or_none()
        
        team2_result = await session.execute(
            select(Team).where(Team.id == match_data.team2_id)
        )
        team2 = team2_result.scalar_one_or_none()
        
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
        await session.commit()
        await session.refresh(match)
        
        return await self._create_elimination_match_response(session, match)
    
    async def get_elimination_matches(
        self,
        session: AsyncSession,
        bracket_id: Optional[int] = None,
        round_number: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> List[EliminationMatchResponse]:
        """Get elimination matches with optional filters."""
        stmt = select(EliminationMatch)
        
        if bracket_id:
            stmt = stmt.where(EliminationMatch.bracket_id == bracket_id)
        if round_number:
            stmt = stmt.where(EliminationMatch.round_number == round_number)
        if status_filter:
            stmt = stmt.where(EliminationMatch.status == status_filter)
        
        result = await session.execute(stmt)
        matches = result.scalars().all()
        
        return [await self._create_elimination_match_response(session, match) for match in matches]
    
    async def get_elimination_match(
        self, 
        session: AsyncSession, 
        match_id: int
    ) -> Optional[EliminationMatchResponse]:
        """Get an elimination match by ID."""
        result = await session.execute(
            select(EliminationMatch).where(EliminationMatch.id == match_id)
        )
        match = result.scalar_one_or_none()
        if not match:
            return None
        
        return await self._create_elimination_match_response(session, match)
    
    async def get_elimination_matches_by_bracket(
        self, 
        session: AsyncSession, 
        bracket_id: int
    ) -> List[EliminationMatchResponse]:
        """Get all matches for a specific elimination bracket."""
        result = await session.execute(
            select(EliminationMatch).where(EliminationMatch.bracket_id == bracket_id)
        )
        matches = result.scalars().all()
        
        return [await self._create_elimination_match_response(session, match) for match in matches]
    
    async def update_elimination_match(
        self, 
        session: AsyncSession, 
        match_id: int, 
        update_data: EliminationMatchUpdate
    ) -> Optional[EliminationMatchResponse]:
        """Update an elimination match."""
        result = await session.execute(
            select(EliminationMatch).where(EliminationMatch.id == match_id)
        )
        match = result.scalar_one_or_none()
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
        await session.commit()
        await session.refresh(match)
        
        return await self._create_elimination_match_response(session, match)
    
    async def start_elimination_match(
        self, 
        session: AsyncSession, 
        match_id: int
    ) -> Optional[EliminationMatchResponse]:
        """Start an elimination match."""
        result = await session.execute(
            select(EliminationMatch).where(EliminationMatch.id == match_id)
        )
        match = result.scalar_one_or_none()
        if not match:
            return None
        
        if match.status != MatchStatus.SCHEDULED.value:
            raise ValueError("Match is not in scheduled status")
        
        match.status = MatchStatus.IN_PROGRESS.value
        match.start_time = datetime.utcnow()
        
        session.add(match)
        await session.commit()
        await session.refresh(match)
        
        return await self._create_elimination_match_response(session, match)
    
    async def complete_elimination_match(
        self, 
        session: AsyncSession, 
        match_id: int, 
        result_data: MatchResultCreate
    ) -> Optional[EliminationMatchResponse]:
        """Complete an elimination match with results."""
        # Validate match result
        validation_result = self.validation_service.validate_match_result(
            result_data.winner_id, 
            {"team1_score": result_data.team1_score, "team2_score": result_data.team2_score}
        )
        if not validation_result.is_valid:
            raise ValueError(f"Invalid match result: {validation_result.errors}")
        
        result = await session.execute(
            select(EliminationMatch).where(EliminationMatch.id == match_id)
        )
        match = result.scalar_one_or_none()
        if not match:
            return None
        
        if match.status != MatchStatus.IN_PROGRESS.value:
            raise ValueError("Match is not in progress")
        
        match.winner_id = result_data.winner_id
        match.scores = {"team1_score": result_data.team1_score, "team2_score": result_data.team2_score}
        match.status = MatchStatus.COMPLETED.value
        match.end_time = datetime.utcnow()
        
        session.add(match)
        await session.commit()
        await session.refresh(match)
        
        return await self._create_elimination_match_response(session, match)
    
    # Utility Methods
    async def get_pending_matches(
        self, 
        session: AsyncSession, 
        tournament_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all pending matches for a tournament."""
        matches = []
        
        # Get pending Swiss matches
        swiss_stmt = select(SwissMatch).join(SwissRound)
        if tournament_id:
            swiss_stmt = swiss_stmt.where(
                and_(
                    SwissRound.tournament_id == tournament_id,
                    SwissMatch.status == MatchStatus.SCHEDULED.value
                )
            )
        else:
            swiss_stmt = swiss_stmt.where(SwissMatch.status == MatchStatus.SCHEDULED.value)
        
        swiss_result = await session.execute(swiss_stmt)
        pending_swiss = swiss_result.scalars().all()
        
        for match in pending_swiss:
            response = await self._create_swiss_match_response(session, match)
            matches.append({
                "id": response.id,
                "type": "swiss",
                "team1_name": response.team1_name,
                "team2_name": response.team2_name,
                "status": response.status.value,
                "scheduled_time": response.scheduled_time,
                "round_number": getattr(match, 'round_number', None)
            })
        
        # Get pending elimination matches
        elimination_stmt = select(EliminationMatch).join(EliminationBracket)
        if tournament_id:
            elimination_stmt = elimination_stmt.where(
                and_(
                    EliminationBracket.tournament_id == tournament_id,
                    EliminationMatch.status == MatchStatus.SCHEDULED.value
                )
            )
        else:
            elimination_stmt = elimination_stmt.where(EliminationMatch.status == MatchStatus.SCHEDULED.value)
        
        elimination_result = await session.execute(elimination_stmt)
        pending_elimination = elimination_result.scalars().all()
        
        for match in pending_elimination:
            response = await self._create_elimination_match_response(session, match)
            matches.append({
                "id": response.id,
                "type": "elimination",
                "team1_name": response.team1_name,
                "team2_name": response.team2_name,
                "status": response.status.value,
                "scheduled_time": response.scheduled_time,
                "round_number": response.round_number
            })
        
        return matches
    
    async def get_match_statistics(
        self, 
        session: AsyncSession, 
        tournament_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get match statistics for a tournament."""
        # Swiss match stats
        swiss_stmt = select(SwissMatch).join(SwissRound)
        if tournament_id:
            swiss_stmt = swiss_stmt.where(SwissRound.tournament_id == tournament_id)
        
        swiss_result = await session.execute(swiss_stmt)
        swiss_matches = swiss_result.scalars().all()
        
        # Elimination match stats
        elimination_stmt = select(EliminationMatch).join(EliminationBracket)
        if tournament_id:
            elimination_stmt = elimination_stmt.where(EliminationBracket.tournament_id == tournament_id)
        
        elimination_result = await session.execute(elimination_stmt)
        elimination_matches = elimination_result.scalars().all()
        
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
    async def _create_swiss_match_response(
        self, 
        session: AsyncSession, 
        match: SwissMatch
    ) -> SwissMatchResponse:
        """Create a Swiss match response with team names."""
        team1_result = await session.execute(
            select(Team).where(Team.id == match.team1_id)
        )
        team1 = team1_result.scalar_one_or_none()
        
        team2_result = await session.execute(
            select(Team).where(Team.id == match.team2_id)
        )
        team2 = team2_result.scalar_one_or_none()
        
        winner = None
        if match.winner_id:
            winner_result = await session.execute(
                select(Team).where(Team.id == match.winner_id)
            )
            winner = winner_result.scalar_one_or_none()
        
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
    
    async def _create_elimination_match_response(
        self, 
        session: AsyncSession, 
        match: EliminationMatch
    ) -> EliminationMatchResponse:
        """Create an elimination match response with team names."""
        team1_result = await session.execute(
            select(Team).where(Team.id == match.team1_id)
        )
        team1 = team1_result.scalar_one_or_none()
        
        team2_result = await session.execute(
            select(Team).where(Team.id == match.team2_id)
        )
        team2 = team2_result.scalar_one_or_none()
        
        winner = None
        if match.winner_id:
            winner_result = await session.execute(
                select(Team).where(Team.id == match.winner_id)
            )
            winner = winner_result.scalar_one_or_none()
        
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
