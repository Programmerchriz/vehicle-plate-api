from threading import Lock
from typing import Any, ClassVar

import numpy as np

from app.config.settings import settings
from app.schemas.recognition import (
  BoundingBox,
  DetectionResult,
)


class PlateDetectionService:
  _model: ClassVar[Any | None] = None
  _model_lock: ClassVar[Lock] = Lock()

  def __init__(
    self,
    model_path: str = settings.YOLO_MODEL_PATH,
  ) -> None:
    self.model_path = model_path

  @property
  def model(self) -> Any:
    if PlateDetectionService._model is None:
      with PlateDetectionService._model_lock:
        if PlateDetectionService._model is None:
          from ultralytics import YOLO

          PlateDetectionService._model = YOLO(
            self.model_path,
          )

    return PlateDetectionService._model

  def detect(
    self,
    image: np.ndarray,
  ) -> DetectionResult | None:
    results = self.model.predict(
      source=image,
      device="cpu",
      verbose=False,
    )

    if not results:
      return None

    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:
      return None

    best_box = max(
      boxes,
      key=lambda box: float(box.conf[0]),
    )

    confidence = float(best_box.conf[0])

    if (
      confidence
      < settings.DETECTION_CONFIDENCE_THRESHOLD
    ):
      return None

    x1, y1, x2, y2 = (
      best_box.xyxy[0]
      .cpu()
      .numpy()
      .astype(int)
    )

    return DetectionResult(
      bounding_box=BoundingBox(
        x1=int(x1),
        y1=int(y1),
        x2=int(x2),
        y2=int(y2),
      ),
      confidence=confidence,
      class_id=int(best_box.cls[0]),
    )