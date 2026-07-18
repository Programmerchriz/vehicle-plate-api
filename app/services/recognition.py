import time

from fastapi import UploadFile

from app.schemas.recognition import (
  BoundingBox,
  RecognitionResponse,
)
from app.services.detector import PlateDetectionService
from app.services.image_processing import ImageProcessingService
from app.services.ocr import OCRService

from app.config.settings import settings


class RecognitionService:
  def __init__(self) -> None:
    self.image_processing = ImageProcessingService()
    self.detector = PlateDetectionService()
    self.ocr = OCRService()

  async def recognize_image(
    self,
    file: UploadFile,
  ) -> RecognitionResponse:
    start_time = time.perf_counter()

    try:
      await self.image_processing.validate_image(file)

      image = await self.image_processing.decode_image(file)
      detection = self.detector.detect(image)

      if detection is None:
        raise ValueError("No license plate detected.")

      bbox = detection.bounding_box

      plate_image = self.image_processing.crop_image(
        image=image,
        x1=bbox.x1,
        y1=bbox.y1,
        x2=bbox.x2,
        y2=bbox.y2,
      )

      plate_image = self.image_processing.to_grayscale(
        plate_image,
      )

      plate_image = self.image_processing.resize(
        plate_image,
        width=settings.PLATE_IMAGE_WIDTH,
        height=settings.PLATE_IMAGE_HEIGHT,
      )

      plate_image = self.image_processing.gaussian_blur(
        plate_image,
      )

      plate_image = self.image_processing.adaptive_threshold(
        plate_image,
      )

      ocr_result = self.ocr.read_text(
        plate_image,
      )

      if not ocr_result.plate_number:
        raise ValueError(
          "Unable to recognize license plate."
        )

    except ValueError:
      raise

    except Exception as exc:
      raise RuntimeError(
        "Recognition pipeline failed."
      ) from exc

    if not ocr_result.plate_number:
      raise ValueError("Unable to recognize license plate.")

    processing_time_ms = (
      time.perf_counter() - start_time
    ) * 1000

    confidence = round(
      (
        detection.confidence +
        ocr_result.confidence
      ) / 2,
      2,
    )

    return RecognitionResponse(
      plate_number=ocr_result.plate_number,
      confidence=confidence,
      bounding_box=BoundingBox(
        x1=bbox.x1,
        y1=bbox.y1,
        x2=bbox.x2,
        y2=bbox.y2,
      ),
      processing_time_ms=round(
        processing_time_ms,
        2,
      ),
    )