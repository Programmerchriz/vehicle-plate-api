import re
from itertools import product

import easyocr
import numpy as np

from app.config.settings import settings
from app.schemas.recognition import (
    OCRCandidate,
    OCRResult,
)


class OCRService:
    # MVP Nigerian formats
    # ABC123DE
    # AB123CDE
    NIGERIAN_PLATE_PATTERNS = (
        re.compile(r"^[A-Z]{3}\d{3}[A-Z]{2}$"),
        re.compile(r"^[A-Z]{2}\d{3}[A-Z]{3}$"),
    )

    # Common OCR mistakes
    OCR_CORRECTIONS = {
        "0": ["0", "O", "Q"],
        "O": ["O", "0", "Q"],

        "1": ["1", "I"],
        "I": ["I", "1"],

        "2": ["2", "Z"],
        "Z": ["Z", "2"],

        "4": ["4", "A"],
        "A": ["A", "4"],

        "5": ["5", "S"],
        "S": ["S", "5", "6"],

        "6": ["6", "G", "S"],
        "G": ["G", "6"],

        "8": ["8", "B"],
        "B": ["B", "8"],
        "H": ["H", "W"],
        "W": ["W", "H"],
    }

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
    
    @staticmethod
    def is_letter(char: str) -> bool:
        return char.isalpha()

    @staticmethod
    def is_digit(char: str) -> bool:
        return char.isdigit()

    def position_score(
        self,
        text: str,
    ) -> int:

        #
        # ABC123DE
        #

        if len(text) != 8:
            return -200

        modern = [
            True,
            True,
            True,
            False,
            False,
            False,
            True,
            True,
        ]

        old = [
            True,
            True,
            False,
            False,
            False,
            True,
            True,
            True,
        ]

        best = -200

        for pattern in (modern, old):
            score = 0

            for index, expect_letter in enumerate(pattern):
                char = text[index]

                if expect_letter:
                    if self.is_letter(char):
                        score += 25
                    else:
                        score -= 25

                else:
                    if self.is_digit(char):
                        score += 25
                    else:
                        score -= 25

            best = max(best, score)

        return best

    def regex_match(
        self,
        text: str,
    ) -> bool:
        return any(
            pattern.fullmatch(text)
            for pattern in self.NIGERIAN_PLATE_PATTERNS
        )

    def generate_candidates(
        self,
        text: str,
    ) -> list[str]:
        """
        Generate only candidates that could satisfy
        Nigerian plate layouts.

        Modern:
            ABC123DE

        Old:
            AB123CDE
        """

        patterns = (
            "LLLDDDLL",
            "LLDDDLLL",
        )

        generated: set[str] = set()

        for pattern in patterns:
            possibilities: list[list[str]] = []

            for index, char in enumerate(text):
                values = self.OCR_CORRECTIONS.get(
                    char,
                    [char],
                )

                #
                # Only keep substitutions matching
                # the expected type.
                #
                if pattern[index] == "L":
                    filtered = [
                        value
                        for value in values
                        if value.isalpha()
                    ]

                else:
                    filtered = [
                        value
                        for value in values
                        if value.isdigit()
                    ]

                #
                # Always keep the original character
                # if nothing matched.
                #
                if not filtered:
                    filtered = [char]

                possibilities.append(filtered)

            generated.update(
                "".join(candidate)
                for candidate in product(*possibilities)
            )

        return list(generated)

    def score_candidate(
        self,
        text: str,
        confidence: float,
    ) -> tuple[int, bool]:

        # Base score from OCR confidence (0-100)
        score = int(confidence * 100)

        regex_ok = self.regex_match(text)

        # Strongly favour valid Nigerian formats.
        if regex_ok:
            score += 200
        else:
            score -= 200

        # We only accept 8-character plates.
        if len(text) == 8:
            score += 30
        else:
            score -= 100

        # Remove known non-plate words.
        if text in self.BLACKLIST:
            score -= 150

        # Reward the expected letter/digit positioning.
        score += self.position_score(text)

        return score, regex_ok

    def read_text(
        self,
        image: np.ndarray,
    ) -> OCRResult:

        results = self.reader.readtext(
            image,
            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        )

        print("\n========== OCR ==========")

        all_candidates: list[OCRCandidate] = []

        for _, raw_text, confidence in results:
            cleaned = self.clean_text(raw_text)
            print(f"{cleaned} ({confidence:.2f})")

            if not cleaned:
                continue

            possible_texts: list[str] = []

            #
            # Already 8 characters
            #
            if len(cleaned) == 8:
                possible_texts.append(cleaned)

            #
            # OCR occasionally mistakes '-' for a letter.
            #
            # Example:
            #
            # KSFE622AE
            #  ↓
            # KSF622AE
            #
            elif len(cleaned) == 9:
                possible_texts.append(
                    cleaned[:3] + cleaned[4:]
                )

                possible_texts.append(
                    cleaned[:2] + cleaned[3:]
                )

            else:
                continue

            #
            # Remove duplicates before scoring.
            #
            variants: set[str] = set()

            for text in possible_texts:
                variants.update(
                    self.generate_candidates(text)
                )

            #
            # Score every generated candidate.
            #
            for candidate in variants:
                score, regex_ok = self.score_candidate(
                    candidate,
                    float(confidence),
                )

                all_candidates.append(
                    OCRCandidate(
                        text=candidate,
                        confidence=float(confidence),
                        score=score,
                        regex_match=regex_ok,
                    )
                )

        print("=========================\n")

        if not all_candidates:
            return OCRResult(
                plate_number="",
                confidence=0.0,
                candidates=[],
            )

        #
        # Keep only the highest scoring instance
        # of each unique candidate.
        #
        ranked: dict[str, OCRCandidate] = {}

        for candidate in all_candidates:
            current = ranked.get(candidate.text)

            if (
                current is None
                or candidate.score > current.score
                or (
                    candidate.score == current.score
                    and candidate.confidence > current.confidence
                )
            ):
                ranked[candidate.text] = candidate

        #
        # Final ranking.
        #
        candidates = sorted(
            ranked.values(),
            key=lambda candidate: (
                candidate.score,
                candidate.regex_match,
                candidate.confidence,
                candidate.text,
            ),
            reverse=True,
        )[:5]

        best = candidates[0]

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
    
# end