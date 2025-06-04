from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class Report(BaseModel):
    """Model for a report definition"""
    report_id: int
    report_name: str
    sql_query: str
    parameters: List[str] = []
    
class ReportResult(BaseModel):
    """Model for report execution results"""
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
