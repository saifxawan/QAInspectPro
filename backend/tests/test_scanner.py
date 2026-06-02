import asyncio
from pathlib import Path
import sys
from unittest.mock import patch, AsyncMock

import pytest

# Ensure the backend package is resolvable when running tests from repo root.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.test_engine import scanner


class DummyResponse:
    def __init__(self, headers=None, content=b"", status_code=200):
        self.headers = headers or {}
        self.content = content
        self.status_code = status_code


@pytest.mark.asyncio
async def test_security_auditor_headers():
    auditor = scanner.SecurityAuditor()
    # Test audit_headers directly without network calls
    headers = {"Server": "nginx/1.18.0"}
    findings, score = await auditor.audit_headers(headers)
    
    # Check that missing headers are detected
    assert score < 100.0
    assert any("Missing Strict-Transport-Security" in f.title for f in findings)
    assert any("Information Disclosure" in f.title for f in findings)


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_performance_analyzer(mock_get):
    # Setup mock return value
    mock_response = DummyResponse(content=b"x" * 1024, status_code=200)
    mock_get.return_value = mock_response
    
    analyzer = scanner.PerformanceAnalyzer()
    metrics = await analyzer.measure_response_time("https://example.com")
    
    assert metrics["status_code"] == 200
    assert metrics["content_length"] == 1024
    assert metrics["score"] >= 0


@pytest.mark.asyncio
@patch("backend.test_engine.scanner.URLScanner.scan_url")
async def test_analyze_target_wrapper(mock_scan):
    # Mock scanner.scan_url to return a pre-configured ScanResult
    mock_scan.return_value = scanner.ScanResult(
        url="https://example.com",
        scan_time=0.5,
        security_score=80.0,
        performance_score=90.0,
        security_findings=[{"title": "Missing Strict-Transport-Security Header", "severity": "high"}],
        performance_metrics=[{"metric": "ttlb", "value": 500.0}],
        recommendations=["Improve security headers"],
        timestamp="2026-05-17T00:00:00"
    )
    
    result = await scanner.analyze_target("https://example.com")
    
    assert result["performance"]["status"] == "Passed"
    assert result["performance"]["load_time_seconds"] == pytest.approx(0.5)
    assert result["security"]["status"] == "Failed"
    assert "Missing Strict-Transport-Security Header" in result["security"]["issues"]
