from sqlalchemy.orm import Session

from app.config.security import (
  create_access_token,
  verify_password,
)
from app.models.user import User


def authenticate_user(
  db: Session,
  email: str,
  password: str,
) -> User | None:
  user = (
    db.query(User)
    .filter(User.email == email)
    .first()
  )

  if user is None:
    return None

  if not verify_password(
    password,
    user.password_hash,
  ):
    return None

  return user


def login_user(
  user: User,
) -> dict[str, str]:
  token = create_access_token(
    str(user.id)
  )

  return {
    "access_token": token,
    "token_type": "bearer",
  }


def logout_user() -> dict[str, str]:
  return {
    "message": "Logged out successfully.",
  }