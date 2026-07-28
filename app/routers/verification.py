from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.verification import VerificationResponse
from app.services.recognition import recognition_service
from app.services.verification import VerificationService


router = APIRouter(
  prefix="/verification",
  tags=["Verification"],
)

# recognition_service = RecognitionService()


def require_verification_role(
  current_user: User = Depends(get_current_user),
) -> User:
  if current_user.role not in {
    UserRole.ADMIN,
    UserRole.OFFICER,
  }:
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
  file: UploadFile = File(...),
  db: Session = Depends(get_db),
  current_user: User = Depends(require_verification_role),
) -> VerificationResponse:
  try:
    recognition_result = await recognition_service.recognize_image(file)

    recognition = (
      VerificationService.extract_recognition_info(
        recognition_result
      )
    )

    return VerificationService.verify_plate(
      db=db,
      plate_number=recognition.detected_plate,
      current_user=current_user,
      recognition=recognition,
    )

  except ValueError as exc:
    raise HTTPException(
      status_code=422,
      detail=str(exc),
    ) from exc

  except RuntimeError as exc:
    raise HTTPException(
      status_code=500,
      detail=str(exc),
    ) from exc