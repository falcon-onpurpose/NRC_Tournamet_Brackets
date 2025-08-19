"""
Bracket service for generating and managing tournament brackets.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models import Tournament, Team, SwissMatch, EliminationMatch, EliminationBracket
from schemas import SwissMatchCreate, EliminationMatchCreate
from services.validation_service import ValidationService


class BracketService:
    """Service for managing tournament brackets."""
    
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self.validation_service = ValidationService()
    
    async def generate_swiss_brackets(self, tournament_id: int, round_number: int, 
                                    session: Optional[AsyncSession] = None) -> List[SwissMatch]:
        """
        Generate Swiss round brackets.
        
        Args:
            tournament_id: Tournament ID
            round_number: Round number
            session: Database session (optional)
            
        Returns:
            List of Swiss matches
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Get tournament and teams
        tournament_stmt = select(Tournament).where(Tournament.id == tournament_id)
        tournament_result = await db_session.execute(tournament_stmt)
        tournament = tournament_result.scalar_one_or_none()
        
        if not tournament:
            raise ValueError(f"Tournament with ID {tournament_id} not found")
        
        teams_stmt = select(Team).where(Team.tournament_id == tournament_id)
        teams_result = await db_session.execute(teams_stmt)
        teams = teams_result.scalars().all()
        
        if len(teams) < 2:
            raise ValueError("At least 2 teams required for Swiss brackets")
        
        # Check if matches already exist for this round
        existing_matches_stmt = select(SwissMatch).where(
            and_(SwissMatch.tournament_id == tournament_id, 
                 SwissMatch.round_number == round_number)
        )
        existing_matches_result = await db_session.execute(existing_matches_stmt)
        existing_matches = existing_matches_result.scalars().all()
        
        if existing_matches:
            raise ValueError(f"Swiss matches already exist for round {round_number}")
        
        # Generate pairings based on round number
        if round_number == 1:
            # First round: random pairing
            matches = self._generate_random_pairings(teams, tournament_id, round_number)
        else:
            # Subsequent rounds: pair by standings
            matches = await self._generate_standings_pairings(
                teams, tournament_id, round_number, db_session
            )
        
        # Create matches in database
        created_matches = []
        for match_data in matches:
            match = SwissMatch(**match_data)
            db_session.add(match)
            created_matches.append(match)
        
        await db_session.commit()
        
        # Refresh matches to get IDs
        for match in created_matches:
            await db_session.refresh(match)
        
        return created_matches
    
    async def generate_elimination_brackets(self, tournament_id: int, bracket_type: str,
                                          session: Optional[AsyncSession] = None) -> List[EliminationMatch]:
        """
        Generate elimination brackets.
        
        Args:
            tournament_id: Tournament ID
            bracket_type: "winners" or "losers"
            session: Database session (optional)
            
        Returns:
            List of elimination matches
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        if bracket_type not in ["winners", "losers"]:
            raise ValueError("Bracket type must be 'winners' or 'losers'")
        
        # Get tournament and teams
        tournament_stmt = select(Tournament).where(Tournament.id == tournament_id)
        tournament_result = await db_session.execute(tournament_stmt)
        tournament = tournament_result.scalar_one_or_none()
        
        if not tournament:
            raise ValueError(f"Tournament with ID {tournament_id} not found")
        
        teams_stmt = select(Team).where(Team.tournament_id == tournament_id)
        teams_result = await db_session.execute(teams_stmt)
        teams = teams_result.scalars().all()
        
        if len(teams) < 2:
            raise ValueError("At least 2 teams required for elimination brackets")
        
        # Check if bracket already exists
        existing_bracket_stmt = select(EliminationBracket).where(
            and_(EliminationBracket.tournament_id == tournament_id,
                 EliminationBracket.bracket_type == bracket_type)
        )
        existing_bracket_result = await db_session.execute(existing_bracket_stmt)
        existing_bracket = existing_bracket_result.scalar_one_or_none()
        
        if existing_bracket:
            raise ValueError(f"{bracket_type.capitalize()} bracket already exists")
        
        # Create bracket
        bracket = EliminationBracket(
            tournament_id=tournament_id,
            bracket_type=bracket_type,
            status="active"
        )
        db_session.add(bracket)
        await db_session.commit()
        await db_session.refresh(bracket)
        
        # Generate matches
        matches = self._generate_elimination_matches(teams, bracket.id, bracket_type)
        
        # Create matches in database
        created_matches = []
        for match_data in matches:
            match = EliminationMatch(**match_data)
            db_session.add(match)
            created_matches.append(match)
        
        await db_session.commit()
        
        # Refresh matches to get IDs
        for match in created_matches:
            await db_session.refresh(match)
        
        return created_matches
    
    def _generate_random_pairings(self, teams: List[Team], tournament_id: int, 
                                round_number: int) -> List[Dict[str, Any]]:
        """Generate random pairings for first round."""
        import random
        
        # Shuffle teams randomly
        shuffled_teams = teams.copy()
        random.shuffle(shuffled_teams)
        
        matches = []
        match_number = 1
        
        # Pair teams
        for i in range(0, len(shuffled_teams), 2):
            if i + 1 < len(shuffled_teams):
                match_data = {
                    "tournament_id": tournament_id,
                    "team1_id": shuffled_teams[i].id,
                    "team2_id": shuffled_teams[i + 1].id,
                    "round_number": round_number,
                    "match_number": match_number,
                    "status": "scheduled"
                }
                matches.append(match_data)
                match_number += 1
            else:
                # Odd number of teams - bye for last team
                match_data = {
                    "tournament_id": tournament_id,
                    "team1_id": shuffled_teams[i].id,
                    "team2_id": None,  # Bye
                    "round_number": round_number,
                    "match_number": match_number,
                    "status": "bye"
                }
                matches.append(match_data)
        
        return matches
    
    async def _generate_standings_pairings(self, teams: List[Team], tournament_id: int,
                                         round_number: int, session: AsyncSession) -> List[Dict[str, Any]]:
        """Generate pairings based on standings for subsequent rounds."""
        # This is a simplified implementation
        # In a real Swiss system, you'd pair teams with similar scores
        # For now, we'll use random pairing again
        
        return self._generate_random_pairings(teams, tournament_id, round_number)
    
    def _generate_elimination_matches(self, teams: List[Team], bracket_id: int, 
                                    bracket_type: str) -> List[Dict[str, Any]]:
        """Generate elimination bracket matches."""
        import random
        
        # Shuffle teams for seeding
        shuffled_teams = teams.copy()
        random.shuffle(shuffled_teams)
        
        matches = []
        match_number = 1
        
        # Generate first round matches
        for i in range(0, len(shuffled_teams), 2):
            if i + 1 < len(shuffled_teams):
                match_data = {
                    "bracket_id": bracket_id,
                    "team1_id": shuffled_teams[i].id,
                    "team2_id": shuffled_teams[i + 1].id,
                    "round_number": 1,
                    "match_number": match_number,
                    "status": "scheduled"
                }
                matches.append(match_data)
                match_number += 1
            else:
                # Odd number of teams - bye for last team
                match_data = {
                    "bracket_id": bracket_id,
                    "team1_id": shuffled_teams[i].id,
                    "team2_id": None,  # Bye
                    "round_number": 1,
                    "match_number": match_number,
                    "status": "bye"
                }
                matches.append(match_data)
        
        return matches
    
    async def get_bracket_matches(self, tournament_id: int, bracket_type: Optional[str] = None,
                                session: Optional[AsyncSession] = None) -> List[Any]:
        """
        Get matches for a tournament bracket.
        
        Args:
            tournament_id: Tournament ID
            bracket_type: Optional bracket type filter
            session: Database session (optional)
            
        Returns:
            List of matches
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        if bracket_type:
            # Get elimination matches
            stmt = select(EliminationMatch).join(EliminationBracket).where(
                and_(EliminationBracket.tournament_id == tournament_id,
                     EliminationBracket.bracket_type == bracket_type)
            )
        else:
            # Get all Swiss matches
            stmt = select(SwissMatch).where(SwissMatch.tournament_id == tournament_id)
        
        result = await db_session.execute(stmt)
        return result.scalars().all()
