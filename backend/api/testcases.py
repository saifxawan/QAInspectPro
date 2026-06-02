from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core import security
from models.models import TestCase, Project

router = APIRouter(prefix="/api/testcases", tags=["testcases"])

@router.get("/")
def get_all_testcases(
    db: Session = Depends(get_db),
    current_user=Depends(security.get_current_active_user),
):
    # Returns testcases grouped by project
    projects = db.query(Project).all()
    result = []
    for p in projects:
        cases = db.query(TestCase).filter(TestCase.project_id == p.id).all()
        # Group cases by category to make it clean for dashboard
        result.append({
            "project_name": p.name,
            "total_cases": len(cases),
            "cases": [
                {
                    "id": f"TC-{c.id}",
                    "title": c.title,
                    "category": c.category,
                    "expected": c.expected_result
                } for c in cases
            ]
        })
    return {"data": result}
