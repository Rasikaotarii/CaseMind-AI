# ===========================================
# CaseMind AI - Report Generation Agent
# ===========================================
# Responsible for aggregating findings from the Document, Image,
# Evidence, and Timeline agents into a single structured investigation
# report, and exporting that report as a downloadable PDF.

from __future__ import annotations

from datetime import datetime

from fpdf import FPDF


class ReportAgent:
    """
    Agent for generating comprehensive investigation reports.

    Collects results from all other agents and produces a structured
    report (as a dict of sections) plus a formatted PDF export.
    """

    def __init__(self):
        """Initialize the Report Agent."""
        self.name = "Report Agent"
        self.description = "Aggregates all agent findings into a professional investigation report."

    def process(
        self,
        case_name: str,
        investigator_name: str,
        investigation_date,
        document_result: dict | None,
        image_results: list[dict] | None,
        evidence_result: dict | None,
        timeline_result: dict | None,
    ) -> dict:
        """
        Assemble a structured investigation report from all agent outputs.

        Returns a dict with all sections needed to render the report in
        the UI and to export it as a PDF. Never raises.
        """
        document_result = document_result or {}
        image_results = image_results or []
        evidence_result = evidence_result or {}
        timeline_result = timeline_result or {}

        return {
            "status": "success",
            "agent": self.name,
            "case_name": case_name or "Untitled Case",
            "investigator_name": investigator_name or "Unassigned",
            "investigation_date": investigation_date,
            "generated_at": datetime.now().strftime("%B %d, %Y at %H:%M"),
            "executive_summary": document_result.get("summary", "") or "No summary available.",
            "confidence_score": document_result.get("confidence_score", 0),
            "timeline": timeline_result.get("timeline", []),
            "people": evidence_result.get("people", []),
            "locations": evidence_result.get("locations", []),
            "objects": evidence_result.get("objects", []),
            "vehicles": evidence_result.get("vehicles", []),
            "weapons": evidence_result.get("weapons", []),
            "potential_evidence": evidence_result.get("potential_evidence", []),
            "contradictions": evidence_result.get("contradictions", []),
            "cross_reference_notes": evidence_result.get("cross_reference_notes", []),
            "recommendations": document_result.get("recommendations", []),
            "risk_score": evidence_result.get("risk_score", 0),
            "risk_level": evidence_result.get("risk_level", "low"),
            "documents_analyzed": evidence_result.get("documents_analyzed", 0),
            "images_analyzed": evidence_result.get("images_analyzed", len(image_results)),
        }

    def build_pdf(self, report: dict) -> bytes:
        """
        Render the report dictionary as a professional PDF document.

        Args:
            report: The dict produced by ``ReportAgent.process``.

        Returns:
            Raw PDF bytes, ready to be offered as a Streamlit download.
        """
        pdf = FPDF(format="A4", unit="mm")
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.add_page()

        # --- Header ---
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(10, 20, 40)
        pdf.cell(0, 12, "CaseMind AI - Investigation Report", ln=True)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(90, 90, 90)
        pdf.cell(0, 6, f"Case: {report.get('case_name', '')}", ln=True)
        pdf.cell(0, 6, f"Investigator: {report.get('investigator_name', '')}", ln=True)
        pdf.cell(0, 6, f"Report generated: {report.get('generated_at', '')}", ln=True)
        pdf.ln(4)
        self._divider(pdf)

        self._section_title(pdf, "Executive Summary")
        self._body_text(pdf, report.get("executive_summary", "N/A"))

        self._section_title(pdf, "Risk Assessment")
        self._body_text(
            pdf,
            f"Overall Risk Level: {report.get('risk_level', 'low').upper()}  "
            f"(Score: {report.get('risk_score', 0)}/100)\n"
            f"AI Confidence: {report.get('confidence_score', 0)}%\n"
            f"Documents analyzed: {report.get('documents_analyzed', 0)}  |  "
            f"Images analyzed: {report.get('images_analyzed', 0)}",
        )

        self._section_title(pdf, "Timeline")
        timeline = report.get("timeline", [])
        if timeline:
            for entry in timeline:
                self._body_text(
                    pdf,
                    f"- [{entry.get('time', 'Unknown')}] {entry.get('event', '')} "
                    f"(Source: {entry.get('source', '')}, Confidence: {entry.get('confidence', 0)}%)",
                )
        else:
            self._body_text(pdf, "No timeline events were identified.")

        self._section_title(pdf, "Important People")
        people = report.get("people", [])
        if people:
            for p in people:
                sources = ", ".join(p.get("sources", [])) if isinstance(p.get("sources"), list) else ""
                self._body_text(pdf, f"- {p.get('name', 'Unknown')} — {p.get('role', '')} ({sources})")
        else:
            self._body_text(pdf, "No key individuals were identified.")

        self._section_title(pdf, "Evidence Summary")
        for label, key in [
            ("Locations", "locations"), ("Objects", "objects"), ("Vehicles", "vehicles"),
            ("Weapons", "weapons"), ("Potential Evidence", "potential_evidence"),
        ]:
            values = report.get(key, [])
            self._body_text(pdf, f"{label}: " + (", ".join(values) if values else "None identified"))

        self._section_title(pdf, "Contradictions & Cross-References")
        contradictions = report.get("contradictions", [])
        cross_refs = report.get("cross_reference_notes", [])
        if contradictions:
            for c in contradictions:
                self._body_text(pdf, f"- {c}")
        if cross_refs:
            for c in cross_refs:
                self._body_text(pdf, f"- {c}")
        if not contradictions and not cross_refs:
            self._body_text(pdf, "No contradictions or cross-reference flags detected.")

        self._section_title(pdf, "Recommendations")
        recs = report.get("recommendations", [])
        if recs:
            for i, r in enumerate(recs, 1):
                self._body_text(pdf, f"{i}. {r}")
        else:
            self._body_text(pdf, "No recommendations were generated.")

        pdf.ln(4)
        self._divider(pdf)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(140, 140, 140)
        pdf.cell(0, 6, "Generated by CaseMind AI - Multi-Agent Investigation Assistant", ln=True)

        return bytes(pdf.output())

    # -------------------------------------------------------------------
    #  Private PDF Helpers
    # -------------------------------------------------------------------

    @staticmethod
    def _section_title(pdf: FPDF, title: str):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(0, 90, 160)
        pdf.cell(0, 9, title, ln=True)
        pdf.set_draw_color(0, 150, 200)
        pdf.set_line_width(0.4)
        y = pdf.get_y()
        pdf.line(10, y, 200, y)
        pdf.ln(2)

    @staticmethod
    def _body_text(pdf: FPDF, text: str):
        pdf.set_font("Helvetica", "", 10.5)
        pdf.set_text_color(30, 30, 30)
        safe_text = (text or "").encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_text)
        pdf.ln(1)

    @staticmethod
    def _divider(pdf: FPDF):
        pdf.set_draw_color(200, 200, 200)
        y = pdf.get_y()
        pdf.line(10, y, 200, y)
        pdf.ln(3)

    def get_status(self) -> str:
        """Return the current status of the Report Agent."""
        return f"{self.name}: Ready"
