"""
Base repository interface for data access operations.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """Base repository interface for CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @abstractmethod
    async def find_by_id(self, entity_id: int) -> Optional[T]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    async def find_all(self, **filters) -> List[T]:
        """Find all entities with optional filters."""
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save entity (create or update)."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: int) -> bool:
        """Check if entity exists."""
        pass


class BaseService(ABC):
    """Base service interface for business logic."""
    
    def __init__(self, repository: BaseRepository):
        self.repository = repository
