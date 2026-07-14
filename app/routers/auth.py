from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import (
  authenticate_user,
  login_user,
)

router = APIRouter(
  prefix="/auth",
  tags=["Authentication"],
)


@router.post(
  "/login",
  response_model=TokenResponse,
)
def login(
  credentials: LoginRequest,
  db: Session = Depends(get_db),
):
  user = authenticate_user(
    db,
    credentials.email,
    credentials.password,
  )

  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid email or password.",
    )

  return login_user(user)


@router.get(
  "/me",
  response_model=UserResponse,
)
def me(
  current_user=Depends(get_current_user),
):
  return current_user