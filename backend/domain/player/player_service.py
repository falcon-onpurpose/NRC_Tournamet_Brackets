"""
Player service for business logic operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from models import Player
from schemas import PlayerCreate, PlayerUpdate, PlayerResponse
from domain.player.player_repository import PlayerRepository
from domain.player.player_validator import PlayerValidator
from domain.shared.repository import BaseService


class PlayerService(BaseService):
    """Service for player business logic operations."""
    
    def __init__(self, repository: PlayerRepository, validator: PlayerValidator):
        super().__init__(repository)
        self.validator = validator
    
    async def create_player(self, player_data: PlayerCreate) -> Player:
        """
        Create a new player.
        
        Args:
            player_data: Player creation data
            
        Returns:
            Created player
            
        Raises:
            ValueError: If validation fails
        """
        # Validate player data
        validation_result = self.validator.validate_player_data(player_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid player data: {validation_result.errors}")
        
        # Check if player name is unique within the team
        name_validation = await self.validator.validate_player_name_unique(
            player_data.first_name, 
            player_data.last_name, 
            player_data.team_id if hasattr(player_data, 'team_id') else 0
        )
        if not name_validation.is_valid:
            raise ValueError(f"Player name validation failed: {name_validation.errors}")
        
        # Check if email is unique (if provided)
        if player_data.email:
            email_validation = await self.validator.validate_player_email_unique(player_data.email)
            if not email_validation.is_valid:
                raise ValueError(f"Player email validation failed: {email_validation.errors}")
        
        # Create player
        player = Player(
            first_name=player_data.first_name,
            last_name=player_data.last_name,
            email=player_data.email,
            team_id=player_data.team_id if hasattr(player_data, 'team_id') else 0,
            created_at=datetime.utcnow()
        )
        
        return await self.repository.save(player)
    
    async def get_player(self, player_id: int) -> Optional[Player]:
        """
        Get player by ID.
        
        Args:
            player_id: Player ID
            
        Returns:
            Player or None if not found
        """
        return await self.repository.find_by_id(player_id)
    
    async def get_players(self, **filters) -> List[Player]:
        """
        Get players with optional filters.
        
        Args:
            **filters: Optional filters (team_id, first_name, last_name, email)
            
        Returns:
            List of players
        """
        return await self.repository.find_all(**filters)
    
    async def get_players_by_team(self, team_id: int) -> List[Player]:
        """
        Get all players for a specific team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of players
        """
        return await self.repository.find_by_team(team_id)
    
    async def search_players(self, search_term: str) -> List[Player]:
        """
        Search players by name.
        
        Args:
            search_term: Search term for first or last name
            
        Returns:
            List of matching players
        """
        return await self.repository.search_by_name(search_term)
    
    async def find_players_by_email(self, email: str) -> List[Player]:
        """
        Find players by email address.
        
        Args:
            email: Email address
            
        Returns:
            List of players with the email
        """
        return await self.repository.find_by_email(email)
    
    async def update_player(self, player_id: int, player_data: PlayerUpdate) -> Optional[Player]:
        """
        Update player.
        
        Args:
            player_id: Player ID
            player_data: Player update data
            
        Returns:
            Updated player or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        # Check if player exists
        player = await self.repository.find_by_id(player_id)
        if not player:
            return None
        
        # Validate update data
        validation_result = self.validator.validate_player_update(player_data)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid player update data: {validation_result.errors}")
        
        # Check name uniqueness if name is being updated
        if (player_data.first_name or player_data.last_name):
            new_first_name = player_data.first_name if player_data.first_name is not None else player.first_name
            new_last_name = player_data.last_name if player_data.last_name is not None else player.last_name
            
            if new_first_name != player.first_name or new_last_name != player.last_name:
                name_validation = await self.validator.validate_player_name_unique(
                    new_first_name, new_last_name, player.team_id, player_id
                )
                if not name_validation.is_valid:
                    raise ValueError(f"Player name validation failed: {name_validation.errors}")
        
        # Check email uniqueness if email is being updated
        if player_data.email is not None and player_data.email != player.email:
            email_validation = await self.validator.validate_player_email_unique(
                player_data.email, player_id
            )
            if not email_validation.is_valid:
                raise ValueError(f"Player email validation failed: {email_validation.errors}")
        
        # Update player fields
        if player_data.first_name is not None:
            player.first_name = player_data.first_name
        if player_data.last_name is not None:
            player.last_name = player_data.last_name
        if player_data.email is not None:
            player.email = player_data.email
        
        return await self.repository.save(player)
    
    async def delete_player(self, player_id: int) -> bool:
        """
        Delete player.
        
        Args:
            player_id: Player ID
            
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(player_id)
    
    async def get_player_by_name(self, first_name: str, last_name: str, team_id: Optional[int] = None) -> Optional[Player]:
        """
        Get player by full name.
        
        Args:
            first_name: Player's first name
            last_name: Player's last name
            team_id: Optional team ID filter
            
        Returns:
            Player or None if not found
        """
        return await self.repository.find_by_name(first_name, last_name, team_id)
    
    async def get_team_player_count(self, team_id: int) -> int:
        """
        Get count of players in a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            Number of players in the team
        """
        return await self.repository.count_by_team(team_id)
    
    async def get_player_statistics(self) -> Dict[str, Any]:
        """
        Get player statistics.
        
        Returns:
            Dictionary with player statistics
        """
        all_players = await self.repository.find_all()
        players_with_email = [p for p in all_players if p.email]
        
        # Group by team
        teams = {}
        for player in all_players:
            if player.team_id not in teams:
                teams[player.team_id] = 0
            teams[player.team_id] += 1
        
        return {
            "total_players": len(all_players),
            "players_with_email": len(players_with_email),
            "players_without_email": len(all_players) - len(players_with_email),
            "teams_with_players": len(teams),
            "average_players_per_team": sum(teams.values()) / len(teams) if teams else 0
        }
