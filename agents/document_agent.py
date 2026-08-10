# ===========================================
# CaseMind AI - Document Analysis Agent
# ===========================================
# Responsible for processing and analyzing text-based documents
# such as PDFs and TXT files submitted as investigation evidence.
#
# Capabilities:
#   - Send extracted document text to Groq (Llama 3.3 70B) for analysis
#   - Return structured JSON with summary, people, locations,
#     dates/times, events, contradictions, and recommendations
#   - Handle API errors gracefully — never raises, always returns a dict


from __future__ import annotations

import json
import re

from utils.groq_client import get_groq_client, GROQ_MODEL

# ---------------------------------------------------------------------------
#  Groq Model Configuration
# ---------------------------------------------------------------------------
_MODEL_NAME = GROQ_MODEL  # "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
#  Investigation Analysis Prompt
# ---------------------------------------------------------------------------
_ANALYSIS_PROMPT = """You are a senior forensic investigation analyst.

Analyze the following document text that was submitted as evidence in an investigation.
Extract structured investigation intelligence and return ONLY valid JSON — no markdown
fences, no commentary, no explanation.

Return this exact JSON structure:

{{
  "summary": "A comprehensive 3-5 sentence summary of the document content and its investigative significance.",
  "people": [
    {{
      "name": "Full name of the individual",
      "role": "Their role, relationship, or relevance to the case"
    }}
  ],
  "locations": ["List of all locations, addresses, or places mentioned"],
  "dates_times": ["List of all dates and times mentioned, in chronological order"],
  "events": ["List of key events described, in chronological order — each entry should be a concise description"],
  "contradictions": ["List of any contradictions, inconsistencies, or suspicious discrepancies found in the text"],
  "recommendations": ["List of recommended next investigative steps based on the evidence"],
  "confidence_score": 0
}}

Rules:
- "confidence_score" must be an integer from 0 to 100 indicating how confident you are in the completeness and accuracy of the extraction.
- Each person must be an object with "name" and "role" fields.
- If a field has no relevant data, use an empty list [] or an empty string "".
- "dates_times" and "events" should be parallel lists of the same length when possible (i.e., dates_times[i] corresponds to events[i]).
- Do NOT wrap the JSON in markdown code fences.
- Return ONLY the JSON object. Nothing else.

=== DOCUMENT TEXT ===

{document_text}
"""


class DocumentAgent:
    """
    Agent for processing and analyzing text-based investigation documents.

    This agent handles PDF and TXT files, extracting relevant information
    and producing structured analysis results for the investigation pipeline.
    Powered by Groq's Llama 3.3 70B model via the OpenAI-compatible SDK.
    """

    def __init__(self):
        """Initialize the Document Agent."""
        self.name = "Document Agent"
        self.description = "Processes and analyzes text documents for investigation evidence."
        self.supported_formats = ["pdf", "txt"]
        self.processed_documents = []

    def analyze(self, text: str) -> dict:
        """
        Analyze extracted document text using the Groq API.

        Sends the text to Groq (Llama 3.3 70B) with a professional
        investigation prompt and parses the structured JSON response.

        Args:
            text: The extracted plain-text content from one or more documents.

        Returns:
            A dictionary with the structured investigation results, or
            an error dictionary if something goes wrong. This method
            never raises — all failures are caught and converted into
            a valid result dictionary.
        """
        if not text or not text.strip():
            return self._empty_result("No text content was found in the uploaded documents.")

        try:
            client = get_groq_client()

            # Build the prompt with the document text inserted
            prompt = _ANALYSIS_PROMPT.format(document_text=text)

            # Call Groq via the OpenAI-compatible chat completions API
            response = client.chat.completions.create(
                model=_MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior forensic investigation analyst. "
                                    "You always respond with ONLY valid JSON, no markdown, no commentary.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            # Extract text from the response
            raw_text = (response.choices[0].message.content or "").strip()

            # Strip markdown code fences if the model wraps the JSON
            raw_text = self._strip_code_fences(raw_text)

            # Parse the JSON response
            try:
                result = json.loads(raw_text)
            except json.JSONDecodeError:
                # Attempt to recover by extracting the outermost JSON object
                recovered = self._extract_json_object(raw_text)
                if recovered is None:
                    return self._error_result(
                        "Failed to parse the AI response as JSON."
                    )
                result = recovered

            if not isinstance(result, dict):
                return self._error_result(
                    "The AI response was valid JSON but not a JSON object."
                )

            # Validate and normalize the result structure
            return self._normalize_result(result)

        except RuntimeError as e:
            # Raised by get_groq_client() if API key is missing
            return self._error_result(str(e))
        except Exception as e:
            return self._error_result(
                f"An error occurred during analysis: {e}"
            )

    # -------------------------------------------------------------------
    #  Private Helpers
    # -------------------------------------------------------------------

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """Remove markdown code fences (```json ... ```) from a string."""
        # Match ```json ... ``` or ``` ... ```
        pattern = r"^```(?:json)?\s*\n?(.*?)\n?\s*```$"
        match = re.match(pattern, text.strip(), re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    @staticmethod
    def _extract_json_object(text: str) -> dict | None:
        """
        Best-effort recovery of a JSON object embedded in a larger string.

        Finds the first '{' and the matching last '}' and attempts to
        parse the substring. Returns None if recovery is not possible.
        """
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
    def _normalize_result(result: dict) -> dict:
        """
        Ensure the result dictionary has all expected keys with correct types.

        Normalizes person entries into ``{"name": ..., "role": ...}`` objects
        if they were returned as plain strings. Never raises — malformed
        or missing fields fall back to safe defaults.
        """

        def _as_list(value) -> list:
            if isinstance(value, list):
                return value
            if value in (None, ""):
                return []
            return [value]

        def _as_str(value) -> str:
            return value if isinstance(value, str) else ("" if value is None else str(value))

        def _as_confidence(value) -> int:
            try:
                score = int(value)
            except (TypeError, ValueError):
                return 0
            return max(0, min(100, score))

        normalized = {
            "status": "success",
            "summary": _as_str(result.get("summary", "")),
            "people": [],
            "locations": [_as_str(v) for v in _as_list(result.get("locations", []))],
            "dates_times": [_as_str(v) for v in _as_list(result.get("dates_times", []))],
            "events": [_as_str(v) for v in _as_list(result.get("events", []))],
            "contradictions": [_as_str(v) for v in _as_list(result.get("contradictions", []))],
            "recommendations": [_as_str(v) for v in _as_list(result.get("recommendations", []))],
            "confidence_score": _as_confidence(result.get("confidence_score", 0)),
        }

        # Normalize people — ensure each entry is a dict with name + role
        raw_people = _as_list(result.get("people", []))
        for person in raw_people:
            if isinstance(person, dict):
                normalized["people"].append({
                    "name": _as_str(person.get("name", "Unknown")) or "Unknown",
                    "role": _as_str(person.get("role", "Not specified")) or "Not specified",
                })
            elif isinstance(person, str):
                normalized["people"].append({
                    "name": person,
                    "role": "Not specified",
                })

        return normalized

    @staticmethod
    def _empty_result(message: str) -> dict:
        """Return a result dict indicating no content was found."""
        return {
            "status": "empty",
            "message": message,
            "summary": "",
            "people": [],
            "locations": [],
            "dates_times": [],
            "events": [],
            "contradictions": [],
            "recommendations": [],
            "confidence_score": 0,
        }

    @staticmethod
    def _error_result(message: str) -> dict:
        """Return a result dict indicating an error occurred."""
        return {
            "status": "error",
            "message": message,
            "summary": "",
            "people": [],
            "locations": [],
            "dates_times": [],
            "events": [],
            "contradictions": [],
            "recommendations": [],
            "confidence_score": 0,
        }

    def get_status(self) -> str:
        """Return the current status of the Document Agent."""
        return f"{self.name}: Ready (Groq AI connected)"
