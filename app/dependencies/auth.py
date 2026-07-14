from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import decode_access_token
from app.models.enums import UserRole
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
  tokenUrl="/auth/login",
)


def get_current_user(
  db: Session = Depends(get_db),
  token: str = Depends(oauth2_scheme),
):
  payload = decode_access_token(token)

  if payload is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid authentication credentials.",
    )

  user = db.get(
    User,
    int(payload["sub"]),
  )

  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="User not found.",
    )

  return user


def require_roles(
  *roles: UserRole,
):
  def dependency(
    current_user: User = Depends(
      get_current_user,
    ),
  ):
    if current_user.role not in roles:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions.",
      )
    
    if not current_user.is_active:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account is inactive.",
      )

    return current_user

  return dependency