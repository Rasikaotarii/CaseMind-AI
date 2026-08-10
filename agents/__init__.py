# ===========================================
# CaseMind AI - Agents Package
# ===========================================
# This package contains all AI investigation agents.
# Each agent handles a specific aspect of the investigation pipeline.
#
# Agents:
#   - DocumentAgent:  Processes and analyzes text documents (PDF, TXT)
#   - ImageAgent:     Analyzes images for visual evidence
#   - ChatAgent:      Handles conversational investigation queries
#   - TimelineAgent:  Constructs event timelines from evidence
#   - EvidenceAgent:  Cross-references and validates evidence
#   - ReportAgent:    Generates comprehensive investigation reports

from agents.document_agent import DocumentAgent
from agents.image_agent import ImageAgent
from agents.chat_agent import ChatAgent
from agents.timeline_agent import TimelineAgent
from agents.evidence_agent import EvidenceAgent
from agents.report_agent import ReportAgent

__all__ = [
    "DocumentAgent",
    "ImageAgent",
    "ChatAgent",
    "TimelineAgent",
    "EvidenceAgent",
    "ReportAgent",
]
