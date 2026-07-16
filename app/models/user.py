from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import UserRole


class User(BaseModel):
  __tablename__ = "users"

  full_name: Mapped[str] = mapped_column(
    String(100),
    nullable=False,
  )

  email: Mapped[str] = mapped_column(
    String(255),
    unique=True,
    index=True,
    nullable=False,
  )

  password_hash: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
  )

  role: Mapped[UserRole] = mapped_column(
    Enum(UserRole, name="user_role"),
    default=UserRole.OFFICER,
    nullable=False,
  )

  is_active: Mapped[bool] = mapped_column(
    Boolean,
    default=True,
    nullable=False,
  )

  registered_vehicles = relationship(
    "Vehicle",
    back_populates="created_by",
  )