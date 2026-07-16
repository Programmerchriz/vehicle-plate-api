from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import VehicleStatus, VehicleType


class VehicleBase(BaseModel):
  plate_number: str = Field(..., min_length=3, max_length=20)
  owner_name: str = Field(..., min_length=2, max_length=100)
  owner_phone: str = Field(..., min_length=7, max_length=20)
  owner_address: str = Field(..., min_length=5, max_length=255)

  vehicle_make: str = Field(..., min_length=2, max_length=50)
  vehicle_model: str = Field(..., min_length=1, max_length=50)
  vehicle_color: str = Field(..., min_length=2, max_length=30)

  vehicle_type: VehicleType

  manufacture_year: int = Field(..., ge=1900)

  registration_date: date
  expiry_date: date

  status: VehicleStatus = VehicleStatus.ACTIVE

  @field_validator("plate_number")
  @classmethod
  def normalize_plate(cls, value: str) -> str:
      return value.strip().upper()

  @field_validator(
      "owner_name",
      "owner_phone",
      "owner_address",
      "vehicle_make",
      "vehicle_model",
      "vehicle_color",
  )
  @classmethod
  def strip_strings(cls, value: str) -> str:
      return value.strip()

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    plate_number: str | None = None
    owner_name: str | None = None
    owner_phone: str | None = None
    owner_address: str | None = None

    vehicle_make: str | None = None
    vehicle_model: str | None = None
    vehicle_color: str | None = None

    vehicle_type: VehicleType | None = None

    manufacture_year: int | None = Field(None, ge=1900)

    registration_date: date | None = None
    expiry_date: date | None = None

    status: VehicleStatus | None = None

    @field_validator("plate_number")
    @classmethod
    def normalize_plate(cls, value: str | None):
        if value is None:
            return value
        return value.strip().upper()

class VehicleResponse(VehicleBase):
    id: int
    created_by_id: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VehicleListResponse(BaseModel):
    items: list[VehicleResponse]

    total: int
    page: int
    page_size: int
    total_pages: int