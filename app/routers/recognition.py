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
from app.services.detector import PlateDetectionService
from app.services.ocr import OCRService


router = APIRouter(
  prefix="/recognition",
  tags=["Recognition"],
)

recognition_service = RecognitionService()


@router.post(
  "/image",
  summary="Recognize a license plate from an uploaded image",
  description=(
    "Uploads a vehicle image, detects the license plate, "
    "extracts the plate number using OCR, and returns "
    "the recognition result."
  ),

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

  # except Exception as exc:
  #   raise HTTPException(
  #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
  #     detail="Failed to process image.",
  #   ) from exc # production

  except Exception as exc:
    import traceback
    traceback.print_exc()

    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(exc),
    ) from exc # temp - development


@router.get(
  "/health",
  summary="Recognition endpoint health check",
  )
async def health() -> dict[str, str]:
  return {
    "status": "healthy" if PlateDetectionService._model else "unhealthy",
    "detector": "ready" if PlateDetectionService._model else "not_loaded",
    "ocr": "ready" if OCRService._reader else "not_loaded",
  }