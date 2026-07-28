from fastapi import (
  APIRouter,
  Depends,
  HTTPException,
  status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.auth import (
  LoginRequest,
  TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth import (
  authenticate_user,
  login_user,
  logout_user,
)


router = APIRouter(
  prefix="/auth",
  tags=["Authentication"],
)


@router.post(
  "/swagger-login",
  response_model=TokenResponse,
)
def swagger_login(
  form_data: OAuth2PasswordRequestForm = Depends(),
  db: Session = Depends(get_db),
) -> TokenResponse:
  user = authenticate_user(
    db=db,
    email=form_data.username,
    password=form_data.password,
  )

  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid email or password.",
      headers={
        "WWW-Authenticate": "Bearer",
      },
    )

  if not user.is_active:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="User account is inactive.",
    )

  return login_user(user)


@router.post(
  "/login",
  response_model=TokenResponse,
)
def login(
  credentials: LoginRequest,
  db: Session = Depends(get_db),
) -> TokenResponse:
  user = authenticate_user(
    db=db,
    email=credentials.email,
    password=credentials.password,
  )

  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid email or password.",
    )

  if not user.is_active:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="User account is inactive.",
    )

  return login_user(user)


@router.post("/logout")
def logout():
  return logout_user()


@router.get(
  "/me",
  response_model=UserResponse,
)
def me(
  current_user=Depends(get_current_user),
):
  return current_user