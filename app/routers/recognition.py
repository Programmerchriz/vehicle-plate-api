from fastapi import (
  APIRouter,
  File,
  HTTPException,
  UploadFile,
  status,
)

from app.schemas.recognition import (
  RecognitionError,
  RecognitionResponse,
)
from app.services.recognition import RecognitionService


router = APIRouter(
  prefix="/recognition",
  tags=["Recognition"],
)

recognition_service = RecognitionService()


@router.post(
  "/image",
  response_model=RecognitionResponse,
  responses={
    status.HTTP_400_BAD_REQUEST: {
      "model": RecognitionError,
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
      "model": RecognitionError,
    },
  },
)
async def recognize_image(
  file: UploadFile = File(...),
) -> RecognitionResponse:
  try:
    return await recognition_service.recognize_image(file)

  except ValueError as exc:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=str(exc),
    ) from exc

  except Exception as exc:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Failed to process image.",
    ) from exc