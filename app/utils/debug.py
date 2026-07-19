from pathlib import Path

import cv2
import numpy as np


DEBUG_DIR = Path("debug")


def save_debug_image(
  filename: str,
  image: np.ndarray,
) -> None:
  DEBUG_DIR.mkdir(exist_ok=True)

  cv2.imwrite(
    str(DEBUG_DIR / filename),
    image,
  )