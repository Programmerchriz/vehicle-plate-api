import time

from fastapi import UploadFile
import logging

from app.schemas.recognition import (
  BoundingBox,
  RecognitionResponse,
)
from app.services.detector import PlateDetectionService
from app.services.image_processing import ImageProcessingService
from app.services.ocr import OCRService

from app.config.settings import settings
from app.utils.debug import save_debug_image


logger = logging.getLogger(__name__)

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

      save_debug_image(
        "1_original.jpg",
        image,
      )

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

      save_debug_image(
        "2_crop.jpg",
        plate_image,
      )

      # plate_image = self.image_processing.crop_plate_number_region(
      #   plate_image,
      # )

      # save_debug_image(
      #   "2_5_plate_number_region.jpg",
      #   plate_image,
      # )

      gray_plate = self.image_processing.to_grayscale(
        plate_image,
      )

      save_debug_image(
        "3_grayscale.jpg",
        gray_plate,
      )

      gray_plate = self.image_processing.resize(
        gray_plate,
        width=settings.PLATE_IMAGE_WIDTH,
      )

      blurred_plate = self.image_processing.gaussian_blur(
        gray_plate,
      )

      threshold_plate = self.image_processing.adaptive_threshold(
        blurred_plate,
      )

      save_debug_image(
        "4_threshold.jpg",
        threshold_plate,
      )

      gray_result = self.ocr.read_text(
        gray_plate,
      )

      threshold_result = self.ocr.read_text(
        threshold_plate,
      )

      ocr_result = max(
        (
          gray_result,
          threshold_result,
        ),
        key=lambda result: result.confidence,
      )

      if not ocr_result.plate_number:
        raise ValueError(
          "Unable to recognize license plate."
        )

    except ValueError:
      raise

    except Exception as exc:
      logger.exception(
        "Recognition pipeline failed."
      )

      raise RuntimeError(
        "Recognition pipeline failed."
      ) from exc

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
      detection_confidence=detection.confidence,
      ocr_confidence=ocr_result.confidence,
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