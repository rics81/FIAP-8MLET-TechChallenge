from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from scripts.database import get_db
from scripts import schemas
from scripts.auth import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    refresh_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

@router.post("/login/", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens
    
    - **username**: ask for system administyrator
    - **password**: ask for system administyrator
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["username"]})
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh/", response_model=schemas.Token)
async def refresh_token(
    token_data: schemas.RefreshTokenRequest
):
    """
    Refresh access token using refresh token
    """
    tokens = refresh_access_token(token_data.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer"
    }