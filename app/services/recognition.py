import logging
import time

from fastapi import UploadFile

from app.config.settings import settings
from app.schemas.recognition import (
    BoundingBox,
    RecognitionResponse,
)
from app.services.detector import PlateDetectionService
from app.services.image_processing import ImageProcessingService
from app.services.ocr import OCRService
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
                raise ValueError(
                    "No license plate detected."
                )

            bbox = detection.bounding_box

            #
            # Crop detected plate
            #
            plate_image = self.image_processing.crop_image(
                image=image,
                x1=bbox.x1,
                y1=bbox.y1,
                x2=bbox.x2,
                y2=bbox.y2,
            )

            save_debug_image(
                "2_plate.jpg",
                plate_image,
            )

            #
            # Pre-processing
            #
            gray = self.image_processing.to_grayscale(
                plate_image,
            )

            gray = self.image_processing.resize(
                gray,
                width=settings.PLATE_IMAGE_WIDTH,
            )

            save_debug_image(
                "3_gray.jpg",
                gray,
            )

            threshold = self.image_processing.adaptive_threshold(
                gray,
            )

            save_debug_image(
                "4_threshold.jpg",
                threshold,
            )

            #
            # OCR
            #
            gray_result = self.ocr.read_text(gray)

            threshold_result = self.ocr.read_text(
                threshold
            )

            #
            # Merge OCR candidates
            #
            all_candidates = (
                gray_result.candidates
                + threshold_result.candidates
            )

            unique_candidates = {}

            for candidate in all_candidates:
                existing = unique_candidates.get(
                    candidate.text
                )

                if (
                    existing is None
                    or candidate.confidence
                    > existing.confidence
                ):
                    unique_candidates[
                        candidate.text
                    ] = candidate

            ranked_candidates = sorted(
                unique_candidates.values(),
                key=lambda candidate: (
                    candidate.confidence
                ),
                reverse=True,
            )[:5]

            if not ranked_candidates:
                raise ValueError(
                    "Unable to recognize license plate."
                )

            best_candidate = ranked_candidates[0]

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
                detection.confidence
                + best_candidate.confidence
            )
            / 2,
            2,
        )

        return RecognitionResponse(
            plate_number=best_candidate.text,
            confidence=confidence,
            detection_confidence=detection.confidence,
            ocr_confidence=best_candidate.confidence,
            candidates=ranked_candidates,
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

recognition_service = RecognitionService()