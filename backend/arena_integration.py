"""
Arena Integration Module for NRC Tournament Program
Handles communication with the arena control system
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .config import settings
from .schemas import ArenaMatchStart, ArenaMatchComplete, ArenaStatus

logger = logging.getLogger(__name__)


class ArenaIntegration:
    """Handles communication with the arena control system"""
    
    def __init__(self):
        self.base_url = settings.ARENA_API_URL
        self.api_key = settings.ARENA_API_KEY
        self.timeout = settings.ARENA_TIMEOUT
        self.connected = False
        self.current_match = None
        self.pit_status = None
        self.last_update = datetime.utcnow()
        
        # HTTP client for arena communication
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def connect(self) -> bool:
        """Test connection to arena system"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.connected = True
                self.last_update = datetime.utcnow()
                logger.info("Connected to arena system")
                return True
            else:
                logger.warning(f"Arena health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to arena system: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from arena system"""
        await self.client.aclose()
        self.connected = False
        logger.info("Disconnected from arena system")
    
    def is_connected(self) -> bool:
        """Check if connected to arena system"""
        return self.connected
    
    async def get_status(self) -> ArenaStatus:
        """Get current arena status"""
        try:
            response = await self.client.get(f"{self.base_url}/status")
            if response.status_code == 200:
                data = response.json()
                self.current_match = data.get("current_match")
                self.pit_status = data.get("pit_status")
                self.last_update = datetime.utcnow()
                return ArenaStatus(
                    connected=True,
                    current_match=self.current_match,
                    pit_status=self.pit_status,
                    last_update=self.last_update
                )
            else:
                logger.warning(f"Failed to get arena status: {response.status_code}")
                return ArenaStatus(
                    connected=False,
                    last_update=self.last_update
                )
        except Exception as e:
            logger.error(f"Error getting arena status: {e}")
            return ArenaStatus(
                connected=False,
                last_update=self.last_update
            )
    
    async def start_match(self, match_params: Dict[str, Any]) -> bool:
        """Start a match in the arena system"""
        try:
            arena_start = ArenaMatchStart(
                match_id=match_params["match_id"],
                duration=match_params.get("duration", 300),
                pit_assignment=match_params.get("pit_assignment"),
                team1_name=match_params.get("team1_name"),
                team2_name=match_params.get("team2_name")
            )
            
            response = await self.client.post(
                f"{self.base_url}/match/start",
                json=arena_start.model_dump()
            )
            
            if response.status_code == 200:
                self.current_match = match_params["match_id"]
                self.last_update = datetime.utcnow()
                logger.info(f"Started match {match_params['match_id']} in arena")
                return True
            else:
                logger.error(f"Failed to start match in arena: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting match in arena: {e}")
            return False
    
    async def complete_match(self, match_id: int, winner_id: Optional[int], scores: Dict[str, Any]) -> bool:
        """Complete a match in the arena system"""
        try:
            arena_complete = ArenaMatchComplete(
                match_id=match_id,
                winner_id=winner_id,
                scores=scores,
                completion_type="manual"  # Can be timeout, reset, or manual
            )
            
            response = await self.client.post(
                f"{self.base_url}/match/complete",
                json=arena_complete.model_dump()
            )
            
            if response.status_code == 200:
                if self.current_match == match_id:
                    self.current_match = None
                self.last_update = datetime.utcnow()
                logger.info(f"Completed match {match_id} in arena")
                return True
            else:
                logger.error(f"Failed to complete match in arena: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error completing match in arena: {e}")
            return False
    
    async def reset_arena(self) -> bool:
        """Reset the arena to idle state"""
        try:
            response = await self.client.post(f"{self.base_url}/reset")
            if response.status_code == 200:
                self.current_match = None
                self.last_update = datetime.utcnow()
                logger.info("Arena reset successfully")
                return True
            else:
                logger.error(f"Failed to reset arena: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error resetting arena: {e}")
            return False
    
    async def get_pit_status(self) -> Optional[str]:
        """Get current pit status"""
        try:
            response = await self.client.get(f"{self.base_url}/pit/status")
            if response.status_code == 200:
                data = response.json()
                self.pit_status = data.get("status")
                return self.pit_status
            else:
                logger.warning(f"Failed to get pit status: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting pit status: {e}")
            return None
    
    async def control_pit(self, action: str) -> bool:
        """Control pit mechanism (open/close)"""
        try:
            response = await self.client.post(
                f"{self.base_url}/pit/control",
                json={"action": action}
            )
            if response.status_code == 200:
                self.last_update = datetime.utcnow()
                logger.info(f"Pit control action '{action}' executed successfully")
                return True
            else:
                logger.error(f"Failed to control pit: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error controlling pit: {e}")
            return False
    
    async def emergency_stop(self) -> bool:
        """Emergency stop for arena system"""
        try:
            response = await self.client.post(f"{self.base_url}/emergency/stop")
            if response.status_code == 200:
                self.current_match = None
                self.last_update = datetime.utcnow()
                logger.warning("Emergency stop executed on arena system")
                return True
            else:
                logger.error(f"Failed to execute emergency stop: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error executing emergency stop: {e}")
            return False
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
