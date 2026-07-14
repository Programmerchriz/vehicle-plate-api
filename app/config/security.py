from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.config.settings import settings

password_hash = PasswordHash(
  (
    Argon2Hasher(),
  ),
)


def hash_password(password: str) -> str:
  return password_hash.hash(password)


def verify_password(
  plain_password: str,
  hashed_password: str,
) -> bool:
  return password_hash.verify(
    plain_password,
    hashed_password,
  )


def create_access_token(subject: str) -> str:
  expire = datetime.now(timezone.utc) + timedelta(
    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
  )

  payload = {
    "sub": subject,
    "exp": expire,
  }

  return jwt.encode(
    payload,
    settings.SECRET_KEY,
    algorithm=settings.ALGORITHM,
  )


def decode_access_token(token: str):
  try:
    return jwt.decode(
      token,
      settings.SECRET_KEY,
      algorithms=[settings.ALGORITHM],
    )
  except JWTError:
    return None