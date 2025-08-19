"""
Arena Integration API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from database import get_session
from services.container import Container, get_container
from services.match_service import MatchService
from schemas import BaseResponse

router = APIRouter()


def get_match_service(
    container: Container = Depends(get_container),
    session: AsyncSession = Depends(get_session)
):
    """Get match service with database session."""
    return container.get_match_service_with_session(session)


@router.get("/status")
async def get_arena_status():
    """Get current arena status."""
    # This will be implemented when arena integration is complete
    return {
        "arena_status": "idle",
        "connected": False,
        "current_match": None,
        "hazards": {
            "pit": "closed",
            "button": "inactive"
        }
    }


@router.post("/connect")
async def connect_to_arena():
    """Connect to arena system."""
    # This will be implemented when arena integration is complete
    return BaseResponse(
        success=True,
        message="Arena connection established"
    )


@router.post("/disconnect")
async def disconnect_from_arena():
    """Disconnect from arena system."""
    # This will be implemented when arena integration is complete
    return BaseResponse(
        success=True,
        message="Arena connection closed"
    )


@router.post("/start-match/{match_id}")
async def start_match_in_arena(
    match_id: int,
    service: MatchService = Depends(get_match_service)
):
    """Start a match in the arena."""
    try:
        # Get match details
        match = await service.get_swiss_match(match_id)
        if not match:
            match = await service.get_elimination_match(match_id)
        
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
        
        # Start the match
        if hasattr(match, 'round_number'):  # Swiss match
            updated_match = await service.start_swiss_match(match_id)
        else:  # Elimination match
            updated_match = await service.start_elimination_match(match_id)
        
        # Send match parameters to arena (placeholder)
        arena_params = {
            "match_id": match_id,
            "duration": 300,  # 5 minutes default
            "pit_activation_time": 60,  # 1 minute remaining
            "button_delay": None,
            "button_duration": None
        }
        
        return {
            "success": True,
            "message": f"Match {match_id} started in arena",
            "match": updated_match,
            "arena_params": arena_params
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/complete-match/{match_id}")
async def complete_match_in_arena(
    match_id: int,
    winner_id: int,
    scores: Dict[str, Any],
    service: MatchService = Depends(get_match_service)
):
    """Complete a match in the arena."""
    try:
        # Get match details
        match = await service.get_swiss_match(match_id)
        if not match:
            match = await service.get_elimination_match(match_id)
        
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
        
        # Complete the match
        if hasattr(match, 'round_number'):  # Swiss match
            updated_match = await service.complete_swiss_match(match_id, {
                "winner_id": winner_id,
                "team1_score": scores.get("team1_score", 0),
                "team2_score": scores.get("team2_score", 0)
            })
        else:  # Elimination match
            updated_match = await service.complete_elimination_match(match_id, {
                "winner_id": winner_id,
                "team1_score": scores.get("team1_score", 0),
                "team2_score": scores.get("team2_score", 0)
            })
        
        return {
            "success": True,
            "message": f"Match {match_id} completed",
            "match": updated_match,
            "winner_id": winner_id
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/reset-arena")
async def reset_arena():
    """Reset the arena to idle state."""
    # This will be implemented when arena integration is complete
    return BaseResponse(
        success=True,
        message="Arena reset to idle state"
    )


@router.post("/configure-hazards")
async def configure_hazards(
    pit_activation_time: Optional[int] = None,
    button_delay: Optional[int] = None,
    button_duration: Optional[int] = None
):
    """Configure arena hazards."""
    # This will be implemented when arena integration is complete
    return BaseResponse(
        success=True,
        message="Hazards configured",
        data={
            "pit_activation_time": pit_activation_time,
            "button_delay": button_delay,
            "button_duration": button_duration
        }
    )


@router.get("/match-queue")
async def get_match_queue(
    tournament_id: Optional[int] = None,
    service: MatchService = Depends(get_match_service)
):
    """Get the queue of upcoming matches for the arena."""
    try:
        matches = await service.get_pending_matches(tournament_id)
        
        # Filter for scheduled matches
        queue = [
            match for match in matches 
            if match.get("status") == "scheduled"
        ][:10]  # Limit to next 10 matches
        
        return {
            "match_queue": queue,
            "queue_length": len(queue)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
