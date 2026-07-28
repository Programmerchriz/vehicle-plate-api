from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import UserRole, VehicleStatus, VehicleType


class VerificationOwnerInfo(BaseModel):
  full_name: str
  phone_number: str | None = None
  email: str | None = None
  address: str | None = None


class VerificationVehicleSummary(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  plate_number: str
  make: str
  model: str
  color: str
  vehicle_type: VehicleType
  manufacture_year: int | None = None
  registration_date: date
  expiry_date: date
  status: VehicleStatus
  created_at: datetime


class PlateRecognitionInfo(BaseModel):
  detected_plate: str
  detection_confidence: float | None = None
  ocr_confidence: float | None = None
  processing_time_ms: float | None = None


class VerificationResponse(BaseModel):
  found: bool
  searched_plate: str
  normalized_plate: str
  message: str
  vehicle: VerificationVehicleSummary | None = None
  owner: VerificationOwnerInfo | None = None
  recognition: PlateRecognitionInfo | None = None


class VerificationRoleContext(BaseModel):
  role: UserRole