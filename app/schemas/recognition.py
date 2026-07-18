from pydantic import BaseModel, ConfigDict, Field


class BoundingBox(BaseModel):
  x1: int
  y1: int
  x2: int
  y2: int


class OCRResult(BaseModel):
  plate_number: str = Field(..., examples=["ABC123XY"])
  confidence: float = Field(..., ge=0.0, le=1.0)


class DetectionResult(BaseModel):
  bounding_box: BoundingBox
  confidence: float = Field(..., ge=0.0, le=1.0)
  class_id: int


class RecognitionResponse(BaseModel):
  plate_number: str
  confidence: float = Field(..., ge=0.0, le=1.0)
  bounding_box: BoundingBox
  processing_time_ms: float

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "plate_number": "ABC123XY",
        "confidence": 0.96,
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


class RecognitionError(BaseModel):
  detail: str

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "detail": "No license plate detected."
      }
    }
  )