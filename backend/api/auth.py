from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from core import security
from core.config import settings
from models import models, schemas

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=schemas.UserOut)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate
):
    """
    Create new user.
    """
    email_exists = db.query(models.User).filter(models.User.email == user_in.email).first()
    username_exists = None
    if user_in.username:
        username_exists = db.query(models.User).filter(models.User.username == user_in.username).first()

    if email_exists:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    if username_exists:
        raise HTTPException(
            status_code=400,
            detail="The username is already taken.",
        )

    db_obj = models.User(
        email=user_in.email,
        username=(user_in.username or user_in.email.split("@")[0]).lower(),
        hashed_password=security.get_password_hash(user_in.password),
        role=user_in.role,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/me", response_model=schemas.UserOut)
def get_current_user(current_user: models.User = Depends(security.get_current_active_user)):
    return current_user
