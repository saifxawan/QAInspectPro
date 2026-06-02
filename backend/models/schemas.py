from pydantic import BaseModel, EmailStr
from typing import Optional, List
from models.models import RoleEnum, StatusEnum
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

# User Schemas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role: RoleEnum = RoleEnum.VIEWER
    is_active: bool = True

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    class Config:
        from_attributes = True

# Scan Schemas
class ScanRequest(BaseModel):
    url: str

class ScanResultSummary(BaseModel):
    target_url: str
    timestamp: str
    system_health_score: int
    summary: dict

# Test Case Schemas
class TestCaseOut(BaseModel):
    id: int
    title: str
    category: str
    expected_result: str
    class Config:
        from_attributes = True
