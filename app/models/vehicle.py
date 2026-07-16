from datetime import date

from sqlalchemy import(
  CheckConstraint,
  Date,
  Enum,
  ForeignKey,
  Integer,
  String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import VehicleStatus, VehicleType


class Vehicle(BaseModel):
  __tablename__ = "vehicles"

  __table_args__ = (
    CheckConstraint(
      "manufacture_year >= 1900",
      name="ck_vehicle_manufacture_year",
    ),
    CheckConstraint(
      "expiry_date >= registration_date",
      name="ck_vehicle_expiry_date",
    ),
  )

  plate_number: Mapped[str] = mapped_column(
      String(20),
      unique=True,
      index=True,
      nullable=False,
  )

  owner_name: Mapped[str] = mapped_column(
      String(100),
      nullable=False,
  )

  owner_phone: Mapped[str] = mapped_column(
      String(20),
      nullable=False,
  )

  owner_address: Mapped[str] = mapped_column(
      String(255),
      nullable=False,
  )

  vehicle_make: Mapped[str] = mapped_column(
      String(50),
      nullable=False,
  )

  vehicle_model: Mapped[str] = mapped_column(
      String(50),
      nullable=False,
  )

  vehicle_color: Mapped[str] = mapped_column(
      String(30),
      nullable=False,
  )

  vehicle_type: Mapped[VehicleType] = mapped_column(
      Enum(VehicleType, name="vehicle_type"),
      nullable=False,
  )

  manufacture_year: Mapped[int] = mapped_column(
      Integer,
      nullable=False,
  )

  registration_date: Mapped[date] = mapped_column(
      Date,
      nullable=False,
  )

  expiry_date: Mapped[date] = mapped_column(
      Date,
      nullable=False,
  )

  status: Mapped[VehicleStatus] = mapped_column(
      Enum(VehicleStatus, name="vehicle_status"),
      default=VehicleStatus.ACTIVE,
      nullable=False,
  )

  created_by_id: Mapped[int] = mapped_column(
      ForeignKey("users.id", ondelete="RESTRICT"),
      nullable=False,
  )

  created_by = relationship(
      "User",
      back_populates="registered_vehicles",
  )