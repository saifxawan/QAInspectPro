from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core import security
from models.models import TestCase, Project, TestResult

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/")
def get_reports_data(
    db: Session = Depends(get_db),
    current_user=Depends(security.get_current_active_user),
):
    projects = db.query(Project).all()
    reports = []
    
    for p in projects:
        cases = db.query(TestCase).filter(TestCase.project_id == p.id).all()
        # Fetch latest result for each case
        case_data = []
        for c in cases:
            # get recent
            last_res = db.query(TestResult).filter(TestResult.test_case_id == c.id).order_by(TestResult.executed_at.desc()).first()
            status = last_res.status.value if last_res else "Skipped"
            notes = last_res.actual_result if last_res and last_res.actual_result else "-"
            
            case_data.append({
                "id": f"TC-{c.id}",
                "title": c.title,
                "category": c.category,
                "expected": c.expected_result,
                "status": status,
                "notes": notes
            })
            
        reports.append({
            "project_name": p.name,
            "total_cases": len(cases),
            "passed": len([c for c in case_data if c["status"] == "Passed"]),
            "failed": len([c for c in case_data if c["status"] == "Failed"]),
            "skipped": len([c for c in case_data if c["status"] == "Skipped"]),
            "cases": case_data
        })
        
    return {"data": reports}
