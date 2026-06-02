"""
Security module for QAInspect Pro
JWT authentication, password hashing, RBAC middleware, and token management
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Generator, Optional, Union, Dict, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.config import settings
from core.database import SessionLocal
from models.models import User, UserRole, AuditLog

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Alias for backward compatibility"""
    return hash_password(password)


def create_access_token(
    subject: Union[str, int],
    user_role: str = "viewer",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        subject: User ID or identifier
        user_role: User's role for RBAC
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    
    to_encode = {
        "sub": str(subject),
        "role": user_role,
        "exp": expire,
        "iat": now,
        "token_type": "access"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, int]) -> str:
    """
    Create JWT refresh token (longer expiry)
    
    Args:
        subject: User ID
        
    Returns:
        Encoded JWT token
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=7)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "token_type": "refresh"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_user(user_id: int, db: Session) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: Optional[str] = payload.get("sub")
        token_type: str = payload.get("token_type", "access")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_id_value = int(user_id)
    except (TypeError, ValueError):
        raise credentials_exception

    user = get_user(user_id_value, db)
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


class RBACChecker:
    """Role-Based Access Control checker"""
    
    # Role hierarchy and permissions
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: [
            "scan:create", "scan:read", "scan:update", "scan:delete",
            "testcase:create", "testcase:read", "testcase:update", "testcase:delete",
            "report:create", "report:read", "report:update", "report:delete", "report:export",
            "user:manage", "system:configure", "audit:view"
        ],
        UserRole.SQA_ENGINEER: [
            "scan:create", "scan:read", "scan:update", "scan:delete",
            "testcase:read", "testcase:update",
            "report:create", "report:read", "report:export"
        ],
        UserRole.ANALYST: [
            "scan:create", "scan:read",
            "testcase:read",
            "report:read", "report:export"
        ],
        UserRole.VIEWER: [
            "scan:read",
            "testcase:read",
            "report:read"
        ]
    }
    
    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        """Check if role has permission"""
        try:
            role_enum = UserRole(role) if isinstance(role, str) else role
            role_perms = RBACChecker.ROLE_PERMISSIONS.get(role_enum, [])
        except (ValueError, KeyError):
            return False
        
        return permission in role_perms
    
    @staticmethod
    def check_permission(role: str, permission: str) -> None:
        """Raise if role doesn't have permission"""
        if not RBACChecker.has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
    
    @staticmethod
    def check_role(role: str, allowed_roles: List[str]) -> None:
        """Check if user has one of allowed roles"""
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role not authorized for this operation"
            )


def verify_permission(
    required_permission: str,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency for checking permissions"""
    RBACChecker.check_permission(current_user.role.value, required_permission)
    return current_user


def verify_admin_role(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_user


def verify_sqa_role(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure user is SQA Engineer or higher"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SQA_ENGINEER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SQA Engineer role required"
        )
    return current_user


def log_audit(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    details: Optional[Dict] = None,
    status: str = "success",
    error_message: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """Create audit log entry"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        status=status,
        error_message=error_message,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()
    return audit_log
