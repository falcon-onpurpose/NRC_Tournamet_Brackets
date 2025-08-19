"""
Robot API endpoints using refactored service structure.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_session
from application.services.service_factory import ServiceFactory
from schemas import RobotCreate, RobotUpdate, RobotResponse

router = APIRouter()


def get_service_factory(session: AsyncSession = Depends(get_session)) -> ServiceFactory:
    """Get service factory dependency."""
    return ServiceFactory(session)


@router.post("/", response_model=RobotResponse, status_code=status.HTTP_201_CREATED)
async def create_robot(
    robot: RobotCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Create a new robot."""
    try:
        service = factory.create_robot_service()
        created_robot = await service.create_robot(robot)
        return created_robot
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[RobotResponse])
async def get_robots(
    team_id: Optional[int] = None,
    robot_class_id: Optional[int] = None,
    waitlist: Optional[bool] = None,
    fee_paid: Optional[bool] = None,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get robots with optional filters."""
    try:
        service = factory.create_robot_service()
        
        filters = {}
        if team_id is not None:
            filters["team_id"] = team_id
        if robot_class_id is not None:
            filters["robot_class_id"] = robot_class_id
        if waitlist is not None:
            filters["waitlist"] = waitlist
        if fee_paid is not None:
            filters["fee_paid"] = fee_paid
        
        robots = await service.get_robots(**filters)
        return robots
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{robot_id}", response_model=RobotResponse)
async def get_robot(
    robot_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get robot by ID."""
    try:
        service = factory.create_robot_service()
        robot = await service.get_robot(robot_id)
        if not robot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot not found")
        return robot
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{robot_id}", response_model=RobotResponse)
async def update_robot(
    robot_id: int,
    robot_update: RobotUpdate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Update robot."""
    try:
        service = factory.create_robot_service()
        updated_robot = await service.update_robot(robot_id, robot_update)
        if not updated_robot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot not found")
        return updated_robot
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{robot_id}")
async def delete_robot(
    robot_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Delete robot."""
    try:
        service = factory.create_robot_service()
        deleted = await service.delete_robot(robot_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot not found")
        return {"message": "Robot deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/team/{team_id}", response_model=List[RobotResponse])
async def get_robots_by_team(
    team_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get all robots for a specific team."""
    try:
        service = factory.create_robot_service()
        robots = await service.get_robots_by_team(team_id)
        return robots
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/class/{robot_class_id}", response_model=List[RobotResponse])
async def get_robots_by_class(
    robot_class_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get all robots in a specific robot class."""
    try:
        service = factory.create_robot_service()
        robots = await service.get_robots_by_class(robot_class_id)
        return robots
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/waitlist/all", response_model=List[RobotResponse])
async def get_waitlisted_robots(
    robot_class_id: Optional[int] = None,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get all robots on the waitlist."""
    try:
        service = factory.create_robot_service()
        robots = await service.get_waitlisted_robots(robot_class_id)
        return robots
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{robot_id}/move-from-waitlist", response_model=RobotResponse)
async def move_robot_from_waitlist(
    robot_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Move robot from waitlist to active status."""
    try:
        service = factory.create_robot_service()
        robot = await service.move_from_waitlist(robot_id)
        if not robot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot not found")
        return robot
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{robot_id}/mark-fee-paid", response_model=RobotResponse)
async def mark_robot_fee_paid(
    robot_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Mark robot fee as paid."""
    try:
        service = factory.create_robot_service()
        robot = await service.mark_fee_paid(robot_id)
        if not robot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot not found")
        return robot
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/summary")
async def get_robot_statistics(
    robot_class_id: Optional[int] = None,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get robot statistics."""
    try:
        service = factory.create_robot_service()
        stats = await service.get_robot_statistics(robot_class_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
