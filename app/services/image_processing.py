import cv2
import numpy as np
from fastapi import UploadFile

from app.config.settings import settings


ALLOWED_IMAGE_TYPES = {
  "image/jpeg",
  "image/png",
  "image/webp",
}


class ImageProcessingService:
  @staticmethod
  async def validate_image(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
      raise ValueError("Unsupported image format. Use jpeg, png or webp")

    contents = await file.read()

    if len(contents) > settings.MAX_IMAGE_SIZE:
      raise ValueError("Image size exceeds 10 MB.")

    await file.seek(0)

  @staticmethod
  async def decode_image(file: UploadFile) -> np.ndarray:
    contents = await file.read()
    await file.seek(0)

    image = cv2.imdecode(
      np.frombuffer(contents, np.uint8),
      cv2.IMREAD_COLOR,
    )

    if image is None:
      raise ValueError("Unable to decode image.")

    return image

  @staticmethod
  def crop_image(
    image: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
  ) -> np.ndarray:
    height, width = image.shape[:2]

    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(width, x2)
    y2 = min(height, y2)

    if x1 >= x2 or y1 >= y2:
      raise ValueError("Invalid plate region detected.")

    return image[y1:y2, x1:x2]

  @staticmethod
  def to_grayscale(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  @staticmethod
  def resize(
    image: np.ndarray,
    width: int,
    height: int,
  ) -> np.ndarray:
    return cv2.resize(
      image,
      (width, height),
      interpolation=cv2.INTER_LINEAR,
    )

  @staticmethod
  def gaussian_blur(
    image: np.ndarray,
    kernel_size: int = 5,
  ) -> np.ndarray:
    return cv2.GaussianBlur(
      image,
      (kernel_size, kernel_size),
      0,
    )

  @staticmethod
  def adaptive_threshold(image: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
      image,
      255,
      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
      cv2.THRESH_BINARY,
      11,
      2,
    )