import re

import easyocr
import numpy as np

from app.config.settings import settings
from app.schemas.recognition import (
  OCRCandidate,
  OCRResult,
)


class OCRService:
  NIGERIAN_PLATE_PATTERNS = (
      # ABC123DE or ABC123DEF
      re.compile(r"^[A-Z]{3}\d{3}[A-Z]{2,3}$"),

      # AA123BCD or AAA123BCD
      re.compile(r"^[A-Z]{2,3}\d{3}[A-Z]{3}$"),
  )

  BLACKLIST = {
    "ABIA",
    "ADAMAWA",
    "AKWAIBOM",
    "ANAMBRA",
    "BAUCHI",
    "BAYELSA",
    "BENUE",
    "BORNO",
    "CROSSRIVER",
    "DELTA",
    "EBONYI",
    "EDO",
    "EKITI",
    "ENUGU",
    "GOMBE",
    "IMO",
    "JIGAWA",
    "KADUNA",
    "KANO",
    "KATSINA",
    "KEBBI",
    "KOGI",
    "KWARA",
    "LAGOS",
    "NASARAWA",
    "NIGER",
    "OGUN",
    "ONDO",
    "OSUN",
    "OYO",
    "PLATEAU",
    "RIVERS",
    "SOKOTO",
    "TARABA",
    "YOBE",
    "ZAMFARA",
    "ABUJA",
    "FCT",
    "FEDERAL",
    "REPUBLIC",
    "NIGERIA",
    "FEDERALREPUBLICOFNIGERIA",
    "NIGERIA",
    "NIGERIAN",
    "LICENSE",
    "LICENCE",
    "PLATE",
    "CENTREOFEXCELLENCE",
    "GODSOWNSTATE",
    "LANDOFBEAUTY",
    "LANDOFPROMISE",
    "LIGHTOFTHENATION",
    "PEARLOFTOURISM",
    "GLORYOFALLLANDS",
    "FOODBASKETOFTHENATION",
    "HOMEOFPEACE",
    "PEOPLESPARADISE",
    "HOMEOFPEACEANDTOURISM",
    "THEBIGHEART",
    "BIGHEART",
    "SALTOFTHENATION",
    "HEARTBEATOFTHENATION",
    "LANDOFHONOUR",
    "COALCITYSTATE",
    "JEWELOFTHESAVANNA",
    "EASTERNHEARTLAND",
    "THENEWWORLD",
    "CENTREOFLEARNING",
    "CENTREOFCOMMERCE",
    "HOMEOFHOSPITALITY",
    "LANDOFEQUITY",
    "CONFLUENCESTATE",
    "STATEOFHARMONY",
    "HOMEOFSOLIDMINERALS",
    "POWERSTATE",
    "GATEWAYSTATE",
    "SUNSHINESTATE",
    "STATEOFTHELIVINGSPRING",
    "PACESTATTER",
    "PACESETTERSTATE",
    "PACESETTER",
    "HOMEOFPEACEANDTOURISM",
    "TREASUREBASEOFTHENATION",
    "SEATOFTHECALIPHATE",
    "NATURESGIFTTOTHENATION",
    "PRIDEOFTHESAHEL",
    "FARMINGISTHESOLUTION",
  }
    
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
      raise RuntimeError(
        "OCR reader has not been initialized."
      )

    return OCRService._reader

  @staticmethod
  def clean_text(text: str) -> str:
    text = text.upper()
    text = re.sub(
      r"[^A-Z0-9]",
      "",
      text,
    )
    return text.strip()

  def score_candidate(
    self,
    text: str,
  ) -> int:
    score = 0

    if any(
      pattern.fullmatch(text)
      for pattern in self.NIGERIAN_PLATE_PATTERNS
    ):
      score += 100

    digit_count = sum(
      char.isdigit()
      for char in text
    )

    if digit_count >= 3:
      score += 30

    if 8 <= len(text) <= 9:
      score += 20
    else:
      return -100

    return score

  def read_text(
    self,
    image: np.ndarray,
  ) -> OCRResult:
    results = self.reader.readtext(
      image,
      allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    )

    print("\n=== OCR RESULTS ===")

    candidates: list[OCRCandidate] = []

    for _, text, confidence in results:
      cleaned = self.clean_text(text)

      print(
        f"{cleaned} ({confidence:.2f})"
      )

      # Skip empty text
      if not cleaned:
        continue

      # Nigerian plate numbers should be 8-9 characters
      if len(cleaned) < 8 or len(cleaned) > 9:
        continue

      # Skip known non-plate words
      if cleaned in self.BLACKLIST:
        continue

      candidates.append(
        OCRCandidate(
          text=cleaned,
          confidence=float(confidence),
        )
      )

    print("===================\n")

    if not candidates:
      return OCRResult(
        plate_number="",
        confidence=0.0,
        candidates=[],
      )

    ranked = sorted(
      candidates,
      key=lambda candidate: (
        self.score_candidate(
          candidate.text,
        ),
        candidate.confidence,
      ),
      reverse=True,
    )

    best = ranked[0]

    if (
      best.confidence
      < settings.OCR_CONFIDENCE_THRESHOLD
    ):
      return OCRResult(
        plate_number="",
        confidence=0.0,
        candidates=candidates,
      )

    return OCRResult(
      plate_number=best.text,
      confidence=best.confidence,
      candidates=candidates,
    )