# ===========================================
# CaseMind AI - Timeline Construction Agent
# ===========================================
# Responsible for constructing a unified chronological event timeline
# from document evidence (dates_times / events pairs) and image
# evidence (visible date/time stamps + OCR text), tagging each entry
# with its evidence source and a confidence value.

from __future__ import annotations

from dateutil import parser as date_parser


class TimelineAgent:
    """
    Agent for constructing a unified investigation event timeline.

    Combines chronological data extracted by the Document Agent with
    date/time stamps detected by the Image Agent into a single,
    source-tagged, best-effort sorted timeline.
    """

    def __init__(self):
        """Initialize the Timeline Agent."""
        self.name = "Timeline Agent"
        self.description = "Constructs a unified chronological timeline from all evidence sources."

    def process(self, document_result: dict | None, image_results: list[dict] | None) -> dict:
        """
        Build a unified timeline from document and image evidence.

        Args:
            document_result: Normalized result dict from ``DocumentAgent.analyze``.
            image_results: List of normalized result dicts from ``ImageAgent.analyze``.

        Returns:
            A dictionary with a sorted list of timeline entries, each
            containing ``time``, ``event``, ``source``, and ``confidence``.
            Never raises.
        """
        document_result = document_result or {}
        image_results = [r for r in (image_results or []) if r.get("status") == "success"]

        entries = []

        # --- From document evidence ---
        dates = document_result.get("dates_times", []) or []
        events = document_result.get("events", []) or []
        max_len = max(len(dates), len(events))
        doc_confidence = document_result.get("confidence_score", 0)
        for i in range(max_len):
            dt = dates[i] if i < len(dates) else "Unknown date"
            ev = events[i] if i < len(events) else "No description"
            entries.append({
                "time": dt,
                "event": ev,
                "source": "Document Evidence",
                "confidence": doc_confidence,
                "_sort_key": self._safe_parse(dt),
            })

        # --- From image evidence ---
        for img in image_results:
            dt_visible = (img.get("date_time_visible") or "").strip()
            if dt_visible:
                ocr_snippet = (img.get("ocr_text") or "").strip()
                summary = img.get("scene_summary") or "Timestamp detected in image evidence."
                entries.append({
                    "time": dt_visible,
                    "event": f"{summary}" + (f" (OCR: \"{ocr_snippet[:80]}\")" if ocr_snippet else ""),
                    "source": f"Image: {img.get('file', 'image')}",
                    "confidence": img.get("confidence_score", 0),
                    "_sort_key": self._safe_parse(dt_visible),
                })

        # --- Sort: parsed dates first (chronological), unparsed pushed to end in original order ---
        dated = [e for e in entries if e["_sort_key"] is not None]
        undated = [e for e in entries if e["_sort_key"] is None]
        dated.sort(key=lambda e: e["_sort_key"])

        ordered = dated + undated
        for e in ordered:
            e.pop("_sort_key", None)

        return {
            "status": "success",
            "agent": self.name,
            "timeline": ordered,
            "total_events": len(ordered),
        }

    # -------------------------------------------------------------------
    #  Private Helpers
    # -------------------------------------------------------------------

    @staticmethod
    def _safe_parse(value: str):
        """Best-effort parse of a free-text date/time string. Returns None on failure."""
        if not value or not isinstance(value, str):
            return None
        try:
            return date_parser.parse(value, fuzzy=True)
        except (ValueError, OverflowError, TypeError):
            return None

    def get_status(self) -> str:
        """Return the current status of the Timeline Agent."""
        return f"{self.name}: Ready"
