import logging
from typing import List, Dict, Any, Optional
import psycopg2
import psycopg2.extras
from fastapi import HTTPException
from ..database import get_db_connection
from ..models.report import Report, ReportResult

logger = logging.getLogger(__name__)

def get_all_reports() -> List[Report]:
    """
    Get all available reports from the database
    
    Returns:
        List[Report]: List of report objects
    """
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT report_id, report_name, sql_query, parameters FROM reports ORDER BY report_name")
            rows = cursor.fetchall()
            
            reports = []
            for row in rows:
                reports.append(Report(
                    report_id=row['report_id'],
                    report_name=row['report_name'],
                    sql_query=row['sql_query'],
                    parameters=row['parameters'] if row['parameters'] else []
                ))
            
            return reports
    except Exception as e:
        logger.error(f"Error retrieving reports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reports: {str(e)}")
    finally:
        if conn:
            conn.close()

def get_report_by_id(report_id: int) -> Optional[Report]:
    """
    Get a specific report by ID
    
    Args:
        report_id (int): ID of the report to retrieve
        
    Returns:
        Optional[Report]: Report object if found, None otherwise
    """
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                "SELECT report_id, report_name, sql_query, parameters FROM reports WHERE report_id = %s",
                (report_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return Report(
                report_id=row['report_id'],
                report_name=row['report_name'],
                sql_query=row['sql_query'],
                parameters=row['parameters'] if row['parameters'] else []
            )
    except Exception as e:
        logger.error(f"Error retrieving report {report_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report: {str(e)}")
    finally:
        if conn:
            conn.close()

def execute_report(report_id: int, params: Dict[str, Any] = None) -> ReportResult:
    """
    Execute a report and return the results
    
    Args:
        report_id (int): ID of the report to execute
        params (Dict[str, Any], optional): Parameters to apply to the report
        
    Returns:
        ReportResult: Results of the report execution
    """
    try:
        # Get the report definition
        report = get_report_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail=f"Report with ID {report_id} not found")
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Execute the SQL query - for now, we don't handle parameterized queries
            # In the future, this could be enhanced to support parameters
            cursor.execute(report.sql_query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Create the result
            result = ReportResult(
                columns=columns,
                rows=rows,
                row_count=len(rows)
            )
            
            return result
    except psycopg2.Error as db_error:
        logger.error(f"Database error executing report {report_id}: {str(db_error)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
    except Exception as e:
        logger.error(f"Error executing report {report_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute report: {str(e)}")
    finally:
        if conn:
            conn.close()
