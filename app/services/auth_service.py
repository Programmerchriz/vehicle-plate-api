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
):
  user = (
    db.query(User)
    .filter(User.email == email)
    .first()
  )

  if not user:
    return None

  if not verify_password(
    password,
    user.password_hash,
  ):
    return None

  return user


def login_user(
  user: User,
):
  token = create_access_token(
    str(user.id),
  )

  return {
    "access_token": token,
    "token_type": "bearer",
  }