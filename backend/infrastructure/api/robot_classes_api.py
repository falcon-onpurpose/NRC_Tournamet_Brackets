"""
Robot class API endpoints using refactored service structure.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_session
from application.services.service_factory import ServiceFactory
from schemas import RobotClassCreate, RobotClassUpdate, RobotClassResponse

router = APIRouter()


def get_service_factory(session: AsyncSession = Depends(get_session)) -> ServiceFactory:
    """Get service factory dependency."""
    return ServiceFactory(session)


@router.post("/", response_model=RobotClassResponse, status_code=status.HTTP_201_CREATED)
async def create_robot_class(
    robot_class: RobotClassCreate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Create a new robot class."""
    try:
        service = factory.create_robot_class_service()
        created_robot_class = await service.create_robot_class(robot_class)
        return created_robot_class
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[RobotClassResponse])
async def get_robot_classes(
    name: Optional[str] = None,
    weight_limit: Optional[int] = None,
    match_duration: Optional[int] = None,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get robot classes with optional filters."""
    try:
        service = factory.create_robot_class_service()
        
        filters = {}
        if name:
            filters["name"] = name
        if weight_limit is not None:
            filters["weight_limit"] = weight_limit
        if match_duration is not None:
            filters["match_duration"] = match_duration
        
        robot_classes = await service.get_robot_classes(**filters)
        return robot_classes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{robot_class_id}", response_model=RobotClassResponse)
async def get_robot_class(
    robot_class_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get robot class by ID."""
    try:
        service = factory.create_robot_class_service()
        robot_class = await service.get_robot_class(robot_class_id)
        if not robot_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot class not found")
        return robot_class
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{robot_class_id}", response_model=RobotClassResponse)
async def update_robot_class(
    robot_class_id: int,
    robot_class_update: RobotClassUpdate,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Update robot class."""
    try:
        service = factory.create_robot_class_service()
        updated_robot_class = await service.update_robot_class(robot_class_id, robot_class_update)
        if not updated_robot_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot class not found")
        return updated_robot_class
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{robot_class_id}")
async def delete_robot_class(
    robot_class_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Delete robot class."""
    try:
        service = factory.create_robot_class_service()
        deleted = await service.delete_robot_class(robot_class_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot class not found")
        return {"message": "Robot class deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/name/{name}", response_model=RobotClassResponse)
async def get_robot_class_by_name(
    name: str,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get robot class by name."""
    try:
        service = factory.create_robot_class_service()
        robot_class = await service.get_robot_class_by_name(name)
        if not robot_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Robot class not found")
        return robot_class
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/weight-range/{min_weight}/{max_weight}", response_model=List[RobotClassResponse])
async def get_robot_classes_by_weight_range(
    min_weight: int,
    max_weight: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get robot classes within a weight range."""
    try:
        service = factory.create_robot_class_service()
        robot_classes = await service.get_robot_classes_by_weight_range(min_weight, max_weight)
        return robot_classes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/active/all", response_model=List[RobotClassResponse])
async def get_active_robot_classes(
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get robot classes that have active robots."""
    try:
        service = factory.create_robot_class_service()
        robot_classes = await service.get_active_robot_classes()
        return robot_classes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/summary")
async def get_robot_class_statistics(
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get robot class statistics."""
    try:
        service = factory.create_robot_class_service()
        stats = await service.get_robot_class_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{robot_class_id}/robot-count")
async def get_robot_count_by_class(
    robot_class_id: int,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Get count of robots in a specific robot class."""
    try:
        service = factory.create_robot_class_service()
        count = await service.get_robot_count_by_class(robot_class_id)
        return {"robot_class_id": robot_class_id, "robot_count": count}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
