"""
Database models for QAInspect Pro - SQLAlchemy ORM definitions
Professional enterprise-grade schema with relationships and validations
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, JSON, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class RoleEnum(str, enum.Enum):
    """User roles matching database case"""
    ADMIN = "ADMIN"
    SQA_ENGINEER = "SQA_ENGINEER"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


class UserRole(str, enum.Enum):
    """User role enumeration compatible with security module"""
    ADMIN = "ADMIN"
    SQA_ENGINEER = "SQA_ENGINEER"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


class ScanType(str, enum.Enum):
    """Scan type enumeration"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    BOTH = "both"


class ScanStatus(str, enum.Enum):
    """Scan execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class StatusEnum(str, enum.Enum):
    """Execution status for test cases and test results"""
    PASSED = "Passed"
    FAILED = "Failed"
    SKIPPED = "Skipped"


class TestCaseStatus(str, enum.Enum):
    """Test case execution status"""
    NOT_RUN = "not_run"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TestCaseCategory(str, enum.Enum):
    """Test case categories"""
    FUNCTIONAL = "functional"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPATIBILITY = "compatibility"


class ResultStatus(str, enum.Enum):
    """Individual result status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INFO = "info"


class User(Base):
    """User model - stores user credentials and roles"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    @property
    def password_hash(self) -> str:
        return self.hashed_password

    @password_hash.setter
    def password_hash(self, value: str):
        self.hashed_password = value

    # Relationships
    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Project(Base):
    """Project model - represents a scanned target URL scope"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(2048), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    test_cases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"


class TestCase(Base):
    """TestCase model - pre-defined quality gates and test definitions"""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    preconditions = Column(Text, nullable=True)
    steps = Column(Text, nullable=True)
    expected_result = Column(Text, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="test_cases")
    results = relationship("TestResult", back_populates="test_case", cascade="all, delete-orphan")
    scan_results = relationship("ScanResult", back_populates="test_case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestCase(id={self.id}, title={self.title}, category={self.category})>"


class TestResult(Base):
    """TestResult model - records execution of specific test cases"""
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False, index=True)
    status = Column(Enum(StatusEnum), nullable=False, index=True)
    actual_result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    screenshot_url = Column(String(1024), nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    test_case = relationship("TestCase", back_populates="results")

    def __repr__(self):
        return f"<TestResult(id={self.id}, test_case_id={self.test_case_id}, status={self.status})>"


class Scan(Base):
    """Scan model - represents a URL scanning execution (expanded schema)"""
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_url = Column(String(2048), nullable=False, index=True)
    scan_type = Column(Enum(ScanType), default=ScanType.BOTH, nullable=False)
    status = Column(Enum(ScanStatus), default=ScanStatus.PENDING, nullable=False, index=True)
    
    # Scores (0-100)
    security_score = Column(Float, nullable=True, default=0.0)
    performance_score = Column(Float, nullable=True, default=0.0)
    overall_score = Column(Float, nullable=True, default=0.0)
    
    # Results stored as JSON
    security_results = Column(JSON, nullable=True)
    performance_results = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Metadata
    execution_time = Column(Float, nullable=True)  # in seconds
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="scans")
    results = relationship("ScanResult", back_populates="scan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scan(id={self.id}, url={self.target_url}, status={self.status})>"


class ScanResult(Base):
    """ScanResult model - individual test result from a scan (expanded schema)"""
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=True, index=True)
    
    # Result status
    result_status = Column(Enum(ResultStatus), nullable=False)
    severity = Column(String(50), nullable=True)  # critical, high, medium, low, info
    
    # Details
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)  # Detailed findings
    remediation = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    scan = relationship("Scan", back_populates="results")
    test_case = relationship("TestCase", back_populates="scan_results")

    def __repr__(self):
        return f"<ScanResult(id={self.id}, scan_id={self.scan_id}, status={self.result_status})>"


class Report(Base):
    """Report model - aggregated scan reports for export/sharing"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scan references (JSON array of scan IDs)
    scan_ids = Column(JSON, nullable=False)  # [1, 2, 3]
    
    # Report metadata
    report_type = Column(String(50), default="executive")  # executive, detailed, summary
    format_type = Column(String(50), default="pdf")  # pdf, csv, json
    
    # Statistics (cached for performance)
    total_scans = Column(Integer, default=0)
    avg_security_score = Column(Float, nullable=True)
    avg_performance_score = Column(Float, nullable=True)
    critical_findings = Column(Integer, default=0)
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    scheduled_at = Column(DateTime, nullable=True)  # For scheduled reports
    exported_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="reports")

    def __repr__(self):
        return f"<Report(id={self.id}, title={self.title}, scans={len(self.scan_ids or [])})>"


class AuditLog(Base):
    """AuditLog model - track all user actions for compliance"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    action = Column(String(100), nullable=False)  # scan_created, report_exported, etc.
    resource_type = Column(String(50), nullable=False)  # scan, report, testcase
    resource_id = Column(Integer, nullable=True)
    
    details = Column(JSON, nullable=True)
    status = Column(String(50), default="success")  # success, failure
    error_message = Column(Text, nullable=True)
    
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"


class SystemHealth(Base):
    """SystemHealth model - track system metrics and performance"""
    __tablename__ = "system_health"

    id = Column(Integer, primary_key=True, index=True)
    
    # Performance metrics
    avg_scan_time = Column(Float, nullable=True)
    active_scans = Column(Integer, default=0)
    total_scans_today = Column(Integer, default=0)
    
    # System stats
    database_size_mb = Column(Float, nullable=True)
    api_uptime_percent = Column(Float, nullable=True)
    
    # Resource usage
    cpu_percent = Column(Float, nullable=True)
    memory_percent = Column(Float, nullable=True)
    disk_percent = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SystemHealth(avg_scan_time={self.avg_scan_time}s)>"
