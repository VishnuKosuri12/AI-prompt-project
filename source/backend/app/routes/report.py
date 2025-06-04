from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from ..services import report
from ..models.report import Report, ReportResult
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("", response_model=List[Report])
async def get_all_reports():
    """Get all available reports"""
    try:
        reports = report.get_all_reports()
        return reports
    except Exception as e:
        logger.error(f"Error fetching reports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}", response_model=Report)
async def get_report(report_id: int):
    """Get a specific report by ID"""
    try:
        report_data = report.get_report_by_id(report_id)
        if not report_data:
            raise HTTPException(status_code=404, detail=f"Report with ID {report_id} not found")
        return report_data
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching report {report_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{report_id}/execute", response_model=ReportResult)
async def execute_report(report_id: int, parameters: Dict[str, Any] = None):
    """Execute a specific report and return the results"""
    try:
        result = report.execute_report(report_id, parameters)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error executing report {report_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
