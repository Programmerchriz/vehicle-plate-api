import re
import easyocr
import numpy as np

from app.schemas.recognition import OCRResult

from app.config.settings import settings


class OCRService:
  _reader: easyocr.Reader | None = None

  def __init__(self) -> None:
    if OCRService._reader is None:
      OCRService._reader = easyocr.Reader(
        ["en"],
        gpu=False,
      )

  @property
  def reader(self) -> easyocr.Reader:
    if OCRService._reader is None:
      raise RuntimeError("OCR reader has not been initialized.")

    return OCRService._reader

  @staticmethod
  def clean_text(text: str) -> str:
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]", "", text)

    return text.strip()

  def read_text(self, image: np.ndarray) -> OCRResult:
    results = self.reader.readtext(image)

    if not results:
      return OCRResult(
        plate_number="",
        confidence=0.0,
      )

    _, text, confidence = max(
      results,
      key=lambda result: result[2],
    )

    if confidence < settings.OCR_CONFIDENCE_THRESHOLD:
      return OCRResult(
        plate_number="",
        confidence=0.0,
      )

    return OCRResult(
      plate_number=self.clean_text(text),
      confidence=float(confidence),
    )