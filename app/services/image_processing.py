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
  
  async def validate_image(self, file: UploadFile) -> None:
    if not file.filename:
      raise ValueError("No image provided.")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
      raise ValueError("Unsupported image format. Use jpeg, png or webp")

    contents = await file.read()

    if len(contents) > settings.MAX_IMAGE_SIZE:
      raise ValueError("Image size exceeds 10 MB.")

    await file.seek(0)

  
  async def decode_image(self, file: UploadFile) -> np.ndarray:
    contents = await file.read()
    await file.seek(0)

    image = cv2.imdecode(
      np.frombuffer(contents, np.uint8),
      cv2.IMREAD_COLOR,
    )

    if image is None:
      raise ValueError("Unable to decode image.")

    return image

  
  def crop_image(
    self,
    image: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
  ) -> np.ndarray:
    height, width = image.shape[:2]

    padding_x = int((x2 - x1) * 0.08)
    padding_y = int((y2 - y1) * 0.08)

    x1 = max(0, x1 - padding_x)
    y1 = max(0, y1 - padding_y)
    x2 = min(width, x2 + padding_x)
    y2 = min(height, y2 + padding_y)

    if x1 >= x2 or y1 >= y2:
      raise ValueError("Invalid plate region detected.")

    return image[y1:y2, x1:x2]

  # def crop_plate_number_region(
  #   self,
  #   image: np.ndarray,
  # ) -> np.ndarray:
  #   height, width = image.shape[:2]

  #   return image[
  #     int(height * 0.28):int(height * 0.82),
  #     int(width * 0.05):int(width * 0.95),
  #   ]
  
  def to_grayscale(self, image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  
  def resize(
    self,
    image: np.ndarray,
    width: int,
  ) -> np.ndarray:
    height, current_width = image.shape[:2]
    scale = width / current_width
    new_height = int(height * scale)

    return cv2.resize(
      image,
      (width, new_height),
      interpolation=cv2.INTER_CUBIC,
    )

  
  def gaussian_blur(
    self,
    image: np.ndarray,
    kernel_size: int = 5,
  ) -> np.ndarray:
    return cv2.GaussianBlur(
      image,
      (kernel_size, kernel_size),
      0,
    )

  
  def adaptive_threshold(self, image: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
      image,
      255,
      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
      cv2.THRESH_BINARY,
      11,
      2,
    )