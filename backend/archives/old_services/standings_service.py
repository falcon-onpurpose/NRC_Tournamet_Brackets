"""
Standings service for calculating tournament standings and bracket progression.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from models import Tournament, Team, SwissMatch, EliminationMatch, EliminationBracket
from services.validation_service import ValidationService


class StandingsService:
    """Service for calculating tournament standings."""
    
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self.validation_service = ValidationService()
    
    async def calculate_swiss_standings(self, tournament_id: int,
                                      session: Optional[AsyncSession] = None) -> List[Dict[str, Any]]:
        """
        Calculate Swiss tournament standings.
        
        Args:
            tournament_id: Tournament ID
            session: Database session (optional)
            
        Returns:
            List of team standings
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Get all teams and their matches
        teams_stmt = select(Team).where(Team.tournament_id == tournament_id)
        teams_result = await db_session.execute(teams_stmt)
        teams = teams_result.scalars().all()
        
        standings = []
        
        for team in teams:
            # Get team's matches
            matches_stmt = select(SwissMatch).where(
                and_(SwissMatch.tournament_id == tournament_id,
                     (SwissMatch.team1_id == team.id) | (SwissMatch.team2_id == team.id))
            )
            matches_result = await db_session.execute(matches_stmt)
            matches = matches_result.scalars().all()
            
            # Calculate team stats
            wins = 0
            losses = 0
            ties = 0
            points = 0
            
            for match in matches:
                if match.status == "completed":
                    if match.winner_id == team.id:
                        wins += 1
                        points += 3
                    elif match.winner_id is None and match.team1_score == match.team2_score:
                        ties += 1
                        points += 1
                    else:
                        losses += 1
            
            # Calculate tiebreakers (simplified)
            # In a real Swiss system, you'd use Buchholz, Sonneborn-Berger, etc.
            tiebreaker = wins * 1000 + ties * 100 + losses * 10
            
            standings.append({
                "team_id": team.id,
                "team_name": team.name,
                "wins": wins,
                "losses": losses,
                "ties": ties,
                "points": points,
                "tiebreaker": tiebreaker,
                "matches_played": wins + losses + ties
            })
        
        # Sort by points (descending), then tiebreaker (descending)
        standings.sort(key=lambda x: (x["points"], x["tiebreaker"]), reverse=True)
        
        # Add rank
        for i, standing in enumerate(standings):
            standing["rank"] = i + 1
        
        return standings
    
    async def calculate_elimination_standings(self, tournament_id: int, bracket_type: str,
                                            session: Optional[AsyncSession] = None) -> List[Dict[str, Any]]:
        """
        Calculate elimination bracket standings.
        
        Args:
            tournament_id: Tournament ID
            bracket_type: "winners" or "losers"
            session: Database session (optional)
            
        Returns:
            List of team standings
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        if bracket_type not in ["winners", "losers"]:
            raise ValueError("Bracket type must be 'winners' or 'losers'")
        
        # Get bracket and matches
        bracket_stmt = select(EliminationBracket).where(
            and_(EliminationBracket.tournament_id == tournament_id,
                 EliminationBracket.bracket_type == bracket_type)
        )
        bracket_result = await db_session.execute(bracket_stmt)
        bracket = bracket_result.scalar_one_or_none()
        
        if not bracket:
            raise ValueError(f"{bracket_type.capitalize()} bracket not found")
        
        matches_stmt = select(EliminationMatch).where(EliminationMatch.bracket_id == bracket.id)
        matches_result = await db_session.execute(matches_stmt)
        matches = matches_result.scalars().all()
        
        # Get all teams in this bracket
        team_ids = set()
        for match in matches:
            if match.team1_id:
                team_ids.add(match.team1_id)
            if match.team2_id:
                team_ids.add(match.team2_id)
        
        teams_stmt = select(Team).where(Team.id.in_(team_ids))
        teams_result = await db_session.execute(teams_stmt)
        teams = teams_result.scalars().all()
        
        standings = []
        
        for team in teams:
            # Get team's matches in this bracket
            team_matches = [m for m in matches if m.team1_id == team.id or m.team2_id == team.id]
            
            wins = 0
            losses = 0
            eliminated = False
            final_round = 0
            
            for match in team_matches:
                if match.status == "completed":
                    if match.winner_id == team.id:
                        wins += 1
                        final_round = max(final_round, match.round_number)
                    else:
                        losses += 1
                        if bracket_type == "losers":
                            eliminated = True
                        final_round = match.round_number
                elif match.status == "bye":
                    wins += 1
                    final_round = max(final_round, match.round_number)
            
            standings.append({
                "team_id": team.id,
                "team_name": team.name,
                "wins": wins,
                "losses": losses,
                "eliminated": eliminated,
                "final_round": final_round,
                "still_active": not eliminated and wins > 0
            })
        
        # Sort by final round (descending), then wins (descending)
        standings.sort(key=lambda x: (x["final_round"], x["wins"]), reverse=True)
        
        # Add rank
        for i, standing in enumerate(standings):
            standing["rank"] = i + 1
        
        return standings
    
    async def get_tournament_standings(self, tournament_id: int,
                                     session: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        Get comprehensive tournament standings.
        
        Args:
            tournament_id: Tournament ID
            session: Database session (optional)
            
        Returns:
            Dictionary with all standings
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Get tournament
        tournament_stmt = select(Tournament).where(Tournament.id == tournament_id)
        tournament_result = await db_session.execute(tournament_stmt)
        tournament = tournament_result.scalar_one_or_none()
        
        if not tournament:
            raise ValueError(f"Tournament with ID {tournament_id} not found")
        
        standings = {
            "tournament_id": tournament_id,
            "tournament_name": tournament.name,
            "format": tournament.format,
            "status": tournament.status
        }
        
        # Add Swiss standings if applicable
        if tournament.format in ["swiss", "hybrid_swiss_elimination"]:
            standings["swiss_standings"] = await self.calculate_swiss_standings(
                tournament_id, db_session
            )
        
        # Add elimination standings if applicable
        if tournament.format in ["single_elimination", "double_elimination", "hybrid_swiss_elimination"]:
            # Check for winners bracket
            winners_bracket_stmt = select(EliminationBracket).where(
                and_(EliminationBracket.tournament_id == tournament_id,
                     EliminationBracket.bracket_type == "winners")
            )
            winners_bracket_result = await db_session.execute(winners_bracket_stmt)
            if winners_bracket_result.scalar_one_or_none():
                standings["winners_bracket"] = await self.calculate_elimination_standings(
                    tournament_id, "winners", db_session
                )
            
            # Check for losers bracket
            losers_bracket_stmt = select(EliminationBracket).where(
                and_(EliminationBracket.tournament_id == tournament_id,
                     EliminationBracket.bracket_type == "losers")
            )
            losers_bracket_result = await db_session.execute(losers_bracket_stmt)
            if losers_bracket_result.scalar_one_or_none():
                standings["losers_bracket"] = await self.calculate_elimination_standings(
                    tournament_id, "losers", db_session
                )
        
        return standings
    
    async def get_team_standings(self, tournament_id: int, team_id: int,
                               session: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        Get standings for a specific team.
        
        Args:
            tournament_id: Tournament ID
            team_id: Team ID
            session: Database session (optional)
            
        Returns:
            Team standings
        """
        db_session = session or self.session
        if not db_session:
            raise ValueError("Database session is required")
        
        # Get team
        team_stmt = select(Team).where(
            and_(Team.id == team_id, Team.tournament_id == tournament_id)
        )
        team_result = await db_session.execute(team_stmt)
        team = team_result.scalar_one_or_none()
        
        if not team:
            raise ValueError(f"Team with ID {team_id} not found in tournament {tournament_id}")
        
        # Get all standings
        all_standings = await self.get_tournament_standings(tournament_id, db_session)
        
        # Find team in each bracket
        team_standings = {
            "team_id": team_id,
            "team_name": team.name,
            "tournament_id": tournament_id
        }
        
        if "swiss_standings" in all_standings:
            for standing in all_standings["swiss_standings"]:
                if standing["team_id"] == team_id:
                    team_standings["swiss"] = standing
                    break
        
        if "winners_bracket" in all_standings:
            for standing in all_standings["winners_bracket"]:
                if standing["team_id"] == team_id:
                    team_standings["winners_bracket"] = standing
                    break
        
        if "losers_bracket" in all_standings:
            for standing in all_standings["losers_bracket"]:
                if standing["team_id"] == team_id:
                    team_standings["losers_bracket"] = standing
                    break
        
        return team_standings
