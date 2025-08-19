"""
Database configuration and setup for NRC Tournament Program
"""

from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy import text
import os
import logging
from contextlib import contextmanager
from typing import Generator
from config import settings
from datetime import datetime

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Database engine creation
def create_database_engine():
    """Create database engine based on configuration"""
    if settings.DATABASE_URL.startswith("sqlite"):
        # SQLite configuration for development/simple deployment
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL configuration for production
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20
        )
    
    return engine

# Create engine instance
engine = create_database_engine()

def create_db_and_tables():
    """Create all database tables"""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        
        # Create default robot classes if they don't exist
        create_default_robot_classes()
        
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def create_default_robot_classes():
    """Create default robot classes for NRC tournaments"""
    from models import RobotClass
    
    default_classes = [
        {
            "name": "150g - Non-Destructive",
            "weight_limit": 150,
            "match_duration": 120,
            "pit_activation_time": 60,
            "button_delay": None,
            "button_duration": None,
            "description": "Antweight non-destructive class"
        },
        {
            "name": "150g - Antweight Destructive",
            "weight_limit": 150,
            "match_duration": 120,
            "pit_activation_time": 60,
            "button_delay": None,
            "button_duration": None,
            "description": "Antweight destructive class"
        },
        {
            "name": "Beetleweight",
            "weight_limit": 1500,
            "match_duration": 180,
            "pit_activation_time": 60,
            "button_delay": None,
            "button_duration": None,
            "description": "Beetleweight class"
        }
    ]
    
    try:
        with Session(engine) as session:
            for class_data in default_classes:
                # Check if class already exists
                existing = session.exec(
                    select(RobotClass).where(RobotClass.name == class_data["name"])
                ).first()
                
                if not existing:
                    robot_class = RobotClass(**class_data)
                    session.add(robot_class)
                    logger.info(f"Created default robot class: {class_data['name']}")
            
            session.commit()
            logger.info("Default robot classes created successfully")
            
    except Exception as e:
        logger.error(f"Error creating default robot classes: {e}")
        # Don't raise here as this is not critical for startup

def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

@contextmanager
def get_session_context():
    """Context manager for database sessions"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def test_database_connection():
    """Test database connection and return status"""
    try:
        with Session(engine) as session:
            result = session.exec(text("SELECT 1"))
            result.fetchone()
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_database_info():
    """Get database information for diagnostics"""
    try:
        with Session(engine) as session:
            # Get database type
            if settings.DATABASE_URL.startswith("sqlite"):
                db_type = "SQLite"
                version_result = session.exec(text("SELECT sqlite_version()"))
                version = version_result.fetchone()[0]
            else:
                db_type = "PostgreSQL"
                version_result = session.exec(text("SELECT version()"))
                version = version_result.fetchone()[0]
            
            # Get table count
            table_count_result = session.exec(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = table_count_result.fetchone()[0]
            
            return {
                "type": db_type,
                "version": version,
                "table_count": table_count,
                "url": settings.DATABASE_URL.replace(settings.DATABASE_PASSWORD, "***") if settings.DATABASE_PASSWORD else settings.DATABASE_URL
            }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {"error": str(e)}

def backup_database(backup_path: str):
    """Create database backup"""
    try:
        if settings.DATABASE_URL.startswith("sqlite"):
            # SQLite backup
            import shutil
            shutil.copy2(settings.DATABASE_URL.replace("sqlite:///", ""), backup_path)
            logger.info(f"SQLite database backed up to: {backup_path}")
        else:
            # PostgreSQL backup
            import subprocess
            cmd = f"pg_dump {settings.DATABASE_URL} > {backup_path}"
            subprocess.run(cmd, shell=True, check=True)
            logger.info(f"PostgreSQL database backed up to: {backup_path}")
        
        return True
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return False

def restore_database(backup_path: str):
    """Restore database from backup"""
    try:
        if settings.DATABASE_URL.startswith("sqlite"):
            # SQLite restore
            import shutil
            shutil.copy2(backup_path, settings.DATABASE_URL.replace("sqlite:///", ""))
            logger.info(f"SQLite database restored from: {backup_path}")
        else:
            # PostgreSQL restore
            import subprocess
            cmd = f"psql {settings.DATABASE_URL} < {backup_path}"
            subprocess.run(cmd, shell=True, check=True)
            logger.info(f"PostgreSQL database restored from: {backup_path}")
        
        return True
    except Exception as e:
        logger.error(f"Database restore failed: {e}")
        return False

# Database health check
def health_check():
    """Comprehensive database health check"""
    try:
        # Test connection
        if not test_database_connection():
            return {"status": "unhealthy", "error": "Database connection failed"}
        
        # Get database info
        db_info = get_database_info()
        if "error" in db_info:
            return {"status": "unhealthy", "error": db_info["error"]}
        
        # Test basic operations
        with Session(engine) as session:
            # Test read operation
            session.exec(text("SELECT 1"))
            
            # Test write operation (if in development mode)
            if settings.DEBUG:
                test_table = "health_check_test"
                session.exec(text(f"CREATE TABLE IF NOT EXISTS {test_table} (id INTEGER PRIMARY KEY)"))
                session.exec(text(f"INSERT INTO {test_table} (id) VALUES (1)"))
                session.exec(text(f"DELETE FROM {test_table} WHERE id = 1"))
                session.exec(text(f"DROP TABLE IF EXISTS {test_table}"))
                session.commit()
        
        return {
            "status": "healthy",
            "database": db_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

# Initialize database on module import
if __name__ == "__main__":
    create_db_and_tables()
    test_database_connection()
    print("Database initialization complete")
