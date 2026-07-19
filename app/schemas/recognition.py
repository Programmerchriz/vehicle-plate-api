from pydantic import BaseModel, ConfigDict, Field

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
  x1: int
  y1: int
  x2: int
  y2: int


class OCRCandidate(BaseModel):
  text: str
  confidence: float = Field(
      ge=0,
      le=1,
  )
  score: int
  regex_match: bool


class OCRResult(BaseModel):
  plate_number: str
  confidence: float
  candidates: list[OCRCandidate]

class RecognitionResponse(BaseModel):
  plate_number: str
  confidence: float
  detection_confidence: float
  ocr_confidence: float

  candidates: list[OCRCandidate]

  bounding_box: BoundingBox
  processing_time_ms: float

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "plate_number": "ABC123XY",
        "confidence": 0.96,
        "detection_confidence": 0.98,
        "ocr_confidence": 0.94,
        "bounding_box": {
          "x1": 245,
          "y1": 318,
          "x2": 468,
          "y2": 392
        },
        "processing_time_ms": 147.53
      }
    }
  )



class DetectionResult(BaseModel):
  bounding_box: BoundingBox
  confidence: float = Field(..., ge=0.0, le=1.0)
  class_id: int


class RecognitionError(BaseModel):
  detail: str

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "detail": "No license plate detected."
      }
    }
  )