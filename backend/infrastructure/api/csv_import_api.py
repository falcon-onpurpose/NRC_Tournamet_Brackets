"""
CSV Import API endpoints using refactored service structure.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from database import get_session
from application.services.service_factory import ServiceFactory
from schemas import CSVImportRequest, CSVImportResponse

router = APIRouter()


def get_service_factory(session: AsyncSession = Depends(get_session)) -> ServiceFactory:
    """Get service factory dependency."""
    return ServiceFactory(session)


@router.post("/tournament/{tournament_id}", response_model=CSVImportResponse)
async def import_tournament_csv(
    tournament_id: int,
    csv_file: UploadFile = File(...),
    strict_mode: bool = False,
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Import tournament data from CSV file."""
    try:
        # Validate file type
        if not csv_file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file"
            )
        
        # Read CSV content
        csv_content = await csv_file.read()
        csv_data = csv_content.decode('utf-8')
        
        # Create import service
        import_service = factory.create_csv_import_service()
        
        # Import data
        result = import_service.import_tournament_data(
            csv_data=csv_data,
            tournament_id=tournament_id,
            strict_mode=strict_mode
        )
        
        # Generate report
        report = import_service.generate_import_report(result)
        
        from datetime import datetime
        
        return CSVImportResponse(
            import_id=1,  # TODO: Generate actual import ID
            status="completed" if result.success else "failed",
            records_processed=result.processed_rows,
            records_successful=result.successful_imports,
            records_failed=len(result.errors),
            error_log={
                "errors": [{
                    "row": error.row,
                    "column": error.column,
                    "severity": error.severity.value,
                    "message": error.message
                } for error in result.errors],
                "warnings": [{
                    "row": warning.row,
                    "column": warning.column,
                    "severity": warning.severity.value,
                    "message": warning.message
                } for warning in result.warnings],
                "report": report,
                "teams_created": len(result.teams_created),
                "robots_created": len(result.robots_created),
                "players_created": len(result.players_created)
            },
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/validate")
async def validate_csv_structure(
    csv_file: UploadFile = File(...),
    factory: ServiceFactory = Depends(get_service_factory)
):
    """Validate CSV structure without importing."""
    try:
        # Validate file type
        if not csv_file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file"
            )
        
        # Read CSV content
        csv_content = await csv_file.read()
        csv_data = csv_content.decode('utf-8')
        
        # Create import service
        import_service = factory.create_csv_import_service()
        
        # Validate structure
        from domain.csv_import.import_result import ImportResult
        result = import_service.csv_parser.validate_csv_structure(csv_data, ImportResult.create_empty())
        
        return {
            "valid": result,
            "errors": [{
                "row": error.row,
                "column": error.column,
                "severity": error.severity.value,
                "message": error.message
            } for error in result.errors] if hasattr(result, 'errors') else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/sample")
async def generate_sample_csv():
    """Generate a sample CSV template."""
    sample_csv = """Team,Robot_Name,Robot_Weightclass,First_Name,Last_Name,Email,Team_Address,Team_Phone,Comments,Waitlist,Robot_Fee_Paid
Sample Team 1,Robot Alpha,150g - Non-Destructive,John,Doe,john.doe@example.com,123 Main St,555-1234,Great robot!,false,true
Sample Team 2,Robot Beta,Beetleweight,Jane,Smith,jane.smith@example.com,456 Oak Ave,555-5678,Another great robot,false,true"""
    
    return {
        "sample_csv": sample_csv,
        "description": "Sample CSV template with all required and optional fields"
    }
