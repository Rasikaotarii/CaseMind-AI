# ===========================================
# CaseMind AI - Image Analysis Agent
# ===========================================
# Responsible for analyzing image-based evidence such as
# photographs, screenshots, and scanned documents using a
# vision-capable Groq model.
#
# Capabilities:
#   - Object / person / vehicle / weapon detection
#   - OCR (text-in-image extraction)
#   - Scene description and forensic evidence flagging
#   - Structured JSON output, risk scoring, confidence scoring

from __future__ import annotations

import base64
import json
import re

from utils.groq_client import (
    get_groq_client,
    GROQ_VISION_MODEL,
    GROQ_VISION_MODEL_FALLBACK,
)

# ---------------------------------------------------------------------------
#  Image Forensic Analysis Prompt
# ---------------------------------------------------------------------------
_IMAGE_ANALYSIS_PROMPT = """You are a senior forensic image analyst working a criminal investigation.

Examine the attached image carefully and return ONLY valid JSON — no markdown fences,
no commentary, no explanation. Use this exact structure:

{
  "people_count": 0,
  "people": ["short description of each person, e.g. 'Adult male, dark jacket'"],
  "objects": ["notable objects visible, e.g. 'Knife', 'Laptop', 'Backpack'"],
  "vehicles": ["vehicles visible, with color/type if identifiable"],
  "weapons": ["any weapons visible, empty list if none"],
  "documents_or_screens": ["any documents, screenshots, phone/laptop screens visible"],
  "license_plates": ["any license plate numbers visible, exactly as read"],
  "date_time_visible": "any date/time stamp visible in the image, or empty string",
  "ocr_text": "all readable text found anywhere in the image, verbatim",
  "scene_summary": "2-3 sentence objective description of the scene",
  "potential_evidence": ["items or details that could be forensically significant"],
  "suspicious_indicators": ["anything unusual, out of place, or concerning"],
  "risk_level": "low | medium | high",
  "confidence_score": 0
}

Rules:
- "confidence_score" is an integer 0-100 reflecting how confident you are in this reading of the image.
- "risk_level" must reflect the presence of weapons, violence indicators, or clearly dangerous/suspicious content.
- If a field has nothing relevant, use an empty list [] or empty string "".
- Do NOT invent details that are not visibly present in the image.
- Return ONLY the JSON object, nothing else.
"""


class ImageAgent:
    """
    Agent for analyzing image-based investigation evidence.

    Processes PNG, JPG, and JPEG files using a Groq vision-capable
    model to extract structured forensic intelligence.
    """

    def __init__(self):
        """Initialize the Image Agent."""
        self.name = "Image Agent"
        self.description = "Analyzes images for visual evidence, OCR text, and forensic indicators."
        self.supported_formats = ["png", "jpg", "jpeg"]
        self.processed_images = []

    def analyze(self, image_bytes: bytes, filename: str = "image") -> dict:
        """
        Analyze a single image and extract structured forensic information.

        Args:
            image_bytes: Raw bytes of the image file.
            filename: Original filename (used for extension / mime detection).

        Returns:
            A dictionary with structured image analysis results. Never
            raises — all failures are caught and converted into a valid
            error result dictionary.
        """
        if not image_bytes:
            return self._empty_result(filename, "The uploaded image contained no data.")

        try:
            client = get_groq_client()
        except RuntimeError as e:
            return self._error_result(filename, str(e))

        mime = self._guess_mime(filename)
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime};base64,{b64_image}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _IMAGE_ANALYSIS_PROMPT},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ]

        raw_text = None
        last_error = None

        for model_name in (GROQ_VISION_MODEL, GROQ_VISION_MODEL_FALLBACK):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.2,
                    max_completion_tokens=1500,
                )
                raw_text = (response.choices[0].message.content or "").strip()
                break
            except Exception as e:  # noqa: BLE001 - try next model on any failure
                last_error = e
                continue

        if raw_text is None:
            return self._error_result(
                filename,
                f"Image analysis failed on all available vision models: {last_error}",
            )

        raw_text = self._strip_code_fences(raw_text)

        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError:
            recovered = self._extract_json_object(raw_text)
            if recovered is None:
                return self._error_result(filename, "Failed to parse the AI response as JSON.")
            result = recovered

        if not isinstance(result, dict):
            return self._error_result(filename, "The AI response was valid JSON but not a JSON object.")

        return self._normalize_result(result, filename)

    # -------------------------------------------------------------------
    #  Private Helpers
    # -------------------------------------------------------------------

    @staticmethod
    def _guess_mime(filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "png"
        if ext in ("jpg", "jpeg"):
            return "image/jpeg"
        return "image/png"

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        pattern = r"^```(?:json)?\s*\n?(.*?)\n?\s*```$"
        match = re.match(pattern, text.strip(), re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    @staticmethod
    def _extract_json_object(text: str) -> dict | None:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        candidate = text[start:end + 1]
        try:
            parsed = json.loads(candidate)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _normalize_result(result: dict, filename: str) -> dict:
        def _as_list(value) -> list:
            if isinstance(value, list):
                return [str(v) for v in value if str(v).strip()]
            if value in (None, ""):
                return []
            return [str(value)]

        def _as_str(value) -> str:
            return value if isinstance(value, str) else ("" if value is None else str(value))

        def _as_int(value, default=0) -> int:
            try:
                return max(0, min(100, int(value)))
            except (TypeError, ValueError):
                return default

        risk = _as_str(result.get("risk_level", "low")).strip().lower()
        if risk not in ("low", "medium", "high"):
            risk = "low"

        return {
            "status": "success",
            "agent": "Image Agent",
            "file": filename,
            "people_count": _as_int(result.get("people_count", 0), 0),
            "people": _as_list(result.get("people", [])),
            "objects": _as_list(result.get("objects", [])),
            "vehicles": _as_list(result.get("vehicles", [])),
            "weapons": _as_list(result.get("weapons", [])),
            "documents_or_screens": _as_list(result.get("documents_or_screens", [])),
            "license_plates": _as_list(result.get("license_plates", [])),
            "date_time_visible": _as_str(result.get("date_time_visible", "")),
            "ocr_text": _as_str(result.get("ocr_text", "")),
            "scene_summary": _as_str(result.get("scene_summary", "")),
            "potential_evidence": _as_list(result.get("potential_evidence", [])),
            "suspicious_indicators": _as_list(result.get("suspicious_indicators", [])),
            "risk_level": risk,
            "confidence_score": _as_int(result.get("confidence_score", 0), 0),
        }

    @staticmethod
    def _empty_result(filename: str, message: str) -> dict:
        return {
            "status": "empty", "agent": "Image Agent", "file": filename, "message": message,
            "people_count": 0, "people": [], "objects": [], "vehicles": [], "weapons": [],
            "documents_or_screens": [], "license_plates": [], "date_time_visible": "",
            "ocr_text": "", "scene_summary": "", "potential_evidence": [],
            "suspicious_indicators": [], "risk_level": "low", "confidence_score": 0,
        }

    @staticmethod
    def _error_result(filename: str, message: str) -> dict:
        return {
            "status": "error", "agent": "Image Agent", "file": filename, "message": message,
            "people_count": 0, "people": [], "objects": [], "vehicles": [], "weapons": [],
            "documents_or_screens": [], "license_plates": [], "date_time_visible": "",
            "ocr_text": "", "scene_summary": "", "potential_evidence": [],
            "suspicious_indicators": [], "risk_level": "low", "confidence_score": 0,
        }

    def get_status(self) -> str:
        """Return the current status of the Image Agent."""
        return f"{self.name}: Ready (Groq Vision connected)"
