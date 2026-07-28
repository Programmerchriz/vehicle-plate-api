from datetime import date

from sqlalchemy.orm import Session

from app.models.enums import UserRole, VehicleStatus
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.verification import (
  PlateRecognitionInfo,
  VerificationOwnerInfo,
  VerificationResponse,
  VerificationVehicleSummary,
)
from app.services.vehicle import VehicleService


class VerificationService:
  @staticmethod
  def normalize_plate_number(
    plate_number: str,
  ) -> str:
    return "".join(
      character
      for character in plate_number.strip().upper()
      if character.isalnum()
    )

  @classmethod
  def verify_plate(
    cls,
    db: Session,
    plate_number: str,
    current_user: User,
    recognition: PlateRecognitionInfo | None = None,
  ) -> VerificationResponse:
    normalized_plate = cls.normalize_plate_number(plate_number)
    vehicle_service = VehicleService(db)
    vehicle = vehicle_service.get_vehicle_by_plate(normalized_plate)

    if vehicle is None:
      return VerificationResponse(
        found=False,
        searched_plate=plate_number,
        normalized_plate=normalized_plate,
        message="Vehicle is not registered.",
        vehicle=None,
        owner=None,
        recognition=recognition,
      )

    effective_status = cls._get_effective_status(vehicle)

    vehicle_summary = VerificationVehicleSummary(
      plate_number=vehicle.plate_number,
      make=vehicle.vehicle_make,
      model=vehicle.vehicle_model,
      color=vehicle.vehicle_color,
      vehicle_type=vehicle.vehicle_type,
      manufacture_year=vehicle.manufacture_year,
      registration_date=vehicle.registration_date,
      expiry_date=vehicle.expiry_date,
      status=effective_status,
      created_at=vehicle.created_at,
    )

    owner = cls._build_owner_info(
      vehicle=vehicle,
      role=current_user.role,
    )

    return VerificationResponse(
      found=True,
      searched_plate=plate_number,
      normalized_plate=normalized_plate,
      message=cls._get_status_message(
        effective_status
      ),
      vehicle=vehicle_summary,
      owner=owner,
      recognition=recognition,
    )

  @staticmethod
  def _get_effective_status(
    vehicle: Vehicle,
  ) -> VehicleStatus:
    if vehicle.expiry_date < date.today():
      return VehicleStatus.EXPIRED

    return vehicle.status

  @staticmethod
  def _get_status_message(
    status: VehicleStatus,
  ) -> str:
    messages = {
      VehicleStatus.ACTIVE:
        "Vehicle registration is active.",
      VehicleStatus.INACTIVE:
        "Vehicle registration is inactive.",
      VehicleStatus.EXPIRED:
        "Vehicle registration has expired.",
      VehicleStatus.SUSPENDED:
        "Vehicle registration is suspended.",
    }

    return messages.get(
      status,
      "Vehicle registration status is unavailable.",
    )

  @staticmethod
  def _build_owner_info(
    vehicle: Vehicle,
    role: UserRole,
  ) -> VerificationOwnerInfo:
    if role == UserRole.ADMIN:
      return VerificationOwnerInfo(
        full_name=vehicle.owner_name,
        phone_number=vehicle.owner_phone,
        email=None,
        address=vehicle.owner_address,
      )

    return VerificationOwnerInfo(
      full_name=vehicle.owner_name,
      phone_number=VerificationService._mask_phone_number(vehicle.owner_phone),
      email=None,
      address=None,
    )

  @staticmethod
  def _mask_phone_number(
    phone_number: str | None,
  ) -> str | None:
    if not phone_number:
      return None

    cleaned = phone_number.strip()

    if len(cleaned) <= 4:
      return "*" * len(cleaned)

    hidden_length = len(cleaned) - 5

    return (
      f"{cleaned[:3]}"
      f"{'*' * hidden_length}"
      f"{cleaned[-2:]}"
    )

  @staticmethod
  def extract_recognition_info(
    recognition_result,
  ) -> PlateRecognitionInfo:
    if isinstance(recognition_result, dict):
      result = recognition_result
    elif hasattr(recognition_result, "model_dump"):
      result = recognition_result.model_dump()
    else:
      result = vars(recognition_result)

    detected_plate = result.get("plate_number")

    if not detected_plate:
      raise ValueError(
        "The recognition engine did not return "
        "a plate number."
      )

    return PlateRecognitionInfo(
      detected_plate=detected_plate,
      detection_confidence=result.get("detection_confidence"),
      ocr_confidence=result.get("ocr_confidence"),
      processing_time_ms=result.get("processing_time_ms"),
    )
