from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.core import security
from app.core.config import settings
from app.database import get_db
from app.schemas.token import Token
from app.schemas.user import User, UserCreate

router = APIRouter()

@router.post("/register", response_model=User)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create new user
    hashed_password = security.get_password_hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: models.User = Depends(security.get_current_active_user)):
    """Get current user"""
    return current_user
