# ===========================================
# CaseMind AI - Evidence Cross-Reference Agent
# ===========================================
# Responsible for cross-referencing and merging evidence from the
# Document Agent (text) and the Image Agent (visual) into a single
# unified evidence picture for the investigation.
#
# This agent is rule-based (no extra LLM call) so merging is fast,
# deterministic, and free — it deduplicates people/objects/locations,
# combines contradictions, and produces a simple risk score.

from __future__ import annotations


class EvidenceAgent:
    """
    Agent for cross-referencing and validating investigation evidence.

    Merges structured output from the Document Agent and the Image
    Agent into one consolidated evidence set for the Timeline and
    Report agents to consume.
    """

    def __init__(self):
        """Initialize the Evidence Agent."""
        self.name = "Evidence Agent"
        self.description = "Cross-references and merges evidence across documents and images."

    def process(self, document_result: dict | None, image_results: list[dict] | None) -> dict:
        """
        Merge document analysis and image analysis into unified evidence.

        Args:
            document_result: Normalized result dict from ``DocumentAgent.analyze``.
            image_results: List of normalized result dicts from ``ImageAgent.analyze``.

        Returns:
            A dictionary containing merged people, objects, locations,
            weapons, contradictions, potential evidence, and a computed
            overall risk score / level. Never raises.
        """
        document_result = document_result or {}
        image_results = [r for r in (image_results or []) if r.get("status") == "success"]

        # --- Merge people (dedupe by name, case-insensitive) ---
        people_by_key = {}
        for p in document_result.get("people", []) or []:
            name = (p.get("name") or "Unknown").strip()
            key = name.lower()
            people_by_key.setdefault(key, {"name": name, "role": p.get("role", ""), "sources": set()})
            people_by_key[key]["sources"].add("Document")

        for img in image_results:
            for desc in img.get("people", []):
                key = desc.strip().lower()
                if key not in people_by_key:
                    people_by_key[key] = {"name": desc, "role": "Person seen in image evidence", "sources": set()}
                people_by_key[key]["sources"].add(f"Image: {img.get('file', 'image')}")

        merged_people = [
            {"name": v["name"], "role": v["role"] or "Not specified", "sources": sorted(v["sources"])}
            for v in people_by_key.values()
        ]

        # --- Merge objects / weapons / vehicles from images ---
        objects, vehicles, weapons, potential_evidence, suspicious = [], [], [], [], []
        for img in image_results:
            objects.extend(img.get("objects", []))
            vehicles.extend(img.get("vehicles", []))
            weapons.extend(img.get("weapons", []))
            potential_evidence.extend(img.get("potential_evidence", []))
            suspicious.extend(img.get("suspicious_indicators", []))

        objects = self._dedupe(objects)
        vehicles = self._dedupe(vehicles)
        weapons = self._dedupe(weapons)
        potential_evidence = self._dedupe(potential_evidence + [
            f"Document evidence: {c}" for c in document_result.get("recommendations", [])[:0]
        ])
        suspicious = self._dedupe(suspicious)

        # --- Merge locations ---
        locations = self._dedupe(document_result.get("locations", []) or [])

        # --- Merge contradictions ---
        contradictions = list(document_result.get("contradictions", []) or [])
        if weapons and not any("weapon" in c.lower() for c in contradictions):
            pass  # weapons are surfaced separately, not treated as a contradiction

        # --- Cross-reference: flag if image OCR text mentions a name not in document people list ---
        cross_reference_notes = []
        doc_names_lower = {p["name"].lower() for p in merged_people if "Document" in p["sources"]}
        for img in image_results:
            ocr = (img.get("ocr_text") or "").lower()
            for name_key in list(doc_names_lower):
                if name_key and name_key in ocr:
                    cross_reference_notes.append(
                        f"'{name_key.title()}' mentioned in document evidence also appears in OCR text of {img.get('file')}."
                    )

        # --- Risk scoring ---
        risk_score = self._compute_risk_score(document_result, image_results, weapons, suspicious)
        if risk_score >= 70:
            risk_level = "high"
        elif risk_score >= 35:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "status": "success",
            "agent": self.name,
            "people": merged_people,
            "locations": locations,
            "objects": objects,
            "vehicles": vehicles,
            "weapons": weapons,
            "potential_evidence": potential_evidence,
            "suspicious_indicators": suspicious,
            "contradictions": contradictions,
            "cross_reference_notes": cross_reference_notes,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "documents_analyzed": 1 if document_result else 0,
            "images_analyzed": len(image_results),
        }

    # -------------------------------------------------------------------
    #  Private Helpers
    # -------------------------------------------------------------------

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        seen = set()
        out = []
        for item in items:
            key = item.strip().lower()
            if key and key not in seen:
                seen.add(key)
                out.append(item.strip())
        return out

    @staticmethod
    def _compute_risk_score(document_result: dict, image_results: list, weapons: list, suspicious: list) -> int:
        score = 0
        score += min(len(document_result.get("contradictions", []) or []) * 8, 32)
        score += min(len(weapons) * 25, 50)
        score += min(len(suspicious) * 10, 30)
        for img in image_results:
            if img.get("risk_level") == "high":
                score += 20
            elif img.get("risk_level") == "medium":
                score += 8
        return max(0, min(100, score))

    def get_status(self) -> str:
        """Return the current status of the Evidence Agent."""
        return f"{self.name}: Ready"
