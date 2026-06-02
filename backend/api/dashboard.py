from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core import security
from models.models import TestResult, StatusEnum, TestCase, Project

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats")
def get_dashboard_stats(
    target_url: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(security.get_current_active_user),
):
    query_tests = db.query(TestResult)
    if target_url:
        normalized_url = target_url.rstrip("/")
        project = db.query(Project).filter(Project.name == normalized_url).first()
        if project:
            query_tests = query_tests.join(TestCase).filter(TestCase.project_id == project.id)
        else:
            return {
                "total_tests": 0,
                "pass_rate": "0%",
                "fail_rate": "0%",
                "system_health": "N/A"
            }

    total_tests = query_tests.count()
    if total_tests == 0:
        return {
            "total_tests": 0,
            "pass_rate": "0%",
            "fail_rate": "0%",
            "system_health": "N/A"
        }
    
    passed_tests = query_tests.filter(TestResult.status == StatusEnum.PASSED).count()
    failed_tests = query_tests.filter(TestResult.status == StatusEnum.FAILED).count()
    
    pass_rate = (passed_tests / total_tests) * 100
    fail_rate = (failed_tests / total_tests) * 100
    
    health_score = int(pass_rate) # Simple aggregate metric
    
    return {
        "total_tests": total_tests,
        "pass_rate": f"{pass_rate:.1f}%",
        "fail_rate": f"{fail_rate:.1f}%",
        "system_health": f"{health_score}/100"
    }

@router.get("/recent-tests")
def get_recent_tests(
    target_url: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(security.get_current_active_user),
):
    query_tests = db.query(TestResult)
    if target_url:
        normalized_url = target_url.rstrip("/")
        project = db.query(Project).filter(Project.name == normalized_url).first()
        if project:
            query_tests = query_tests.join(TestCase).filter(TestCase.project_id == project.id)
        else:
            return {"data": []}

    recent = query_tests.order_by(TestResult.executed_at.desc()).limit(20).all()
    results_list = []
    for r in recent:
        tc = r.test_case
        results_list.append({
            "id": f"TC-{tc.id}",
            "title": tc.title,
            "category": tc.category,
            "status": r.status.value,
            "execution_time": r.actual_result.split("Time: ")[-1] if r.actual_result and "Time" in r.actual_result else "-",
            "executed_at": r.executed_at.isoformat(),
            "actual": r.actual_result,
            "expected": tc.expected_result,
            "error": r.error_message
        })
    return {"data": results_list}
