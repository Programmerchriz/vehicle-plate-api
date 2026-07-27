from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.verification import VerificationResponse
from app.services.recognition import RecognitionService
from app.services.verification import VerificationService


router = APIRouter(
  prefix="/verification",
  tags=["Verification"],
)


def require_verification_role(
  current_user: User = Depends(get_current_user),
) -> User:
  allowed_roles = {
    UserRole.ADMIN,
    UserRole.OFFICER,
  }

  if current_user.role not in allowed_roles:
    raise HTTPException(
      status_code=403,
      detail="You do not have permission to verify vehicles.",
    )

  return current_user


@router.get(
  "/{plate_number}",
  response_model=VerificationResponse,
)
def verify_plate_number(
  plate_number: str,
  db: Session = Depends(get_db),
  current_user: User = Depends(require_verification_role),
) -> VerificationResponse:
  normalized_plate = VerificationService.normalize_plate_number(
    plate_number
  )

  if not normalized_plate:
    raise HTTPException(
      status_code=422,
      detail="A valid plate number is required.",
    )

  return VerificationService.verify_plate(
    db=db,
    plate_number=plate_number,
    current_user=current_user,
  )


@router.post(
  "/image",
  response_model=VerificationResponse,
)
async def verify_plate_image(
  image: UploadFile = File(...),
  db: Session = Depends(get_db),
  current_user: User = Depends(require_verification_role),
) -> VerificationResponse:
  if not image.content_type:
    raise HTTPException(
      status_code=400,
      detail="Unable to determine the uploaded file type.",
    )

  if not image.content_type.startswith("image/"):
    raise HTTPException(
      status_code=415,
      detail="Only image files are supported.",
    )

  image_bytes = await image.read()

  if not image_bytes:
    raise HTTPException(
      status_code=400,
      detail="The uploaded image is empty.",
    )

  try:
    recognition_result = await run_recognition(image_bytes)

    recognition = VerificationService.extract_recognition_info(
      recognition_result
    )

    return VerificationService.verify_plate(
      db=db,
      plate_number=recognition.detected_plate,
      current_user=current_user,
      recognition=recognition,
    )
  except ValueError as error:
    raise HTTPException(
      status_code=422,
      detail=str(error),
    ) from error
  except HTTPException:
    raise
  except Exception as error:
    raise HTTPException(
      status_code=500,
      detail="Vehicle recognition and verification failed.",
    ) from error


async def run_recognition(
  image_bytes: bytes,
) -> Any:
  """
  Supports common method names so this router can reuse the existing
  Phase 2 recognition service without duplicating the pipeline.
  """

  method_names = (
    "recognize_image",
    "process_image",
    "recognize",
  )

  for method_name in method_names:
    method = getattr(
      RecognitionService,
      method_name,
      None,
    )

    if not method:
      continue

    result = method(image_bytes)

    if hasattr(result, "__await__"):
      return await result

    return result

  raise RuntimeError(
    "No compatible recognition method was found on recognition_service."
  )