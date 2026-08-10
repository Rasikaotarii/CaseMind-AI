# =============================================================================
# CaseMind AI — Main Application
# =============================================================================
# An AI Investigation Assistant that helps investigators analyze evidence.
#
# This file contains the Streamlit UI for:
#   - Home page with branding and description
#   - Sidebar for case creation and configuration
#   - File upload section for evidence submission
#   - Investigation progress tracker
#   - Dashboard with investigation metric cards
#   - Live AI activity panel
#   - Investigation results populated by Groq AI analysis
# =============================================================================

import time as _time

import streamlit as st
from datetime import date, datetime

from agents.document_agent import DocumentAgent
from agents.image_agent import ImageAgent
from agents.evidence_agent import EvidenceAgent
from agents.timeline_agent import TimelineAgent
from agents.report_agent import ReportAgent
from utils.file_handler import (
    extract_all_text,
    has_document_files,
    get_image_files,
    has_image_files,
    read_image_bytes,
)
from utils.groq_client import is_groq_configured as is_groq_configured


# ---------------------------------------------------------------------------
#  Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CaseMind AI — Investigation Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
#  Custom CSS — Premium Dark Investigation Theme
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
#  Custom CSS — Premium Cyber-Forensics Theme
# ---------------------------------------------------------------------------
def inject_custom_css():
    """Inject the full custom CSS theme into the Streamlit app."""

    st.markdown(
        """
        <style>
        /* ===== Import Fonts ===== */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700;800;900&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        /* ===== Root Variables — Cyber-Forensics Palette ===== */
        :root {
            --bg-primary:       #050816;
            --bg-secondary:     #0A0F24;
            --bg-card:          rgba(14, 20, 40, 0.65);
            --bg-card-hover:    rgba(20, 28, 54, 0.8);
            --bg-terminal:      #05070F;
            --border-color:     rgba(0, 229, 255, 0.18);
            --border-glow:      #00E5FF;
            --accent-blue:      #2979FF;
            --accent-cyan:      #00E5FF;
            --accent-purple:    #A855F7;
            --accent-emerald:   #22C55E;
            --accent-amber:     #FACC15;
            --accent-rose:      #FB3B5A;
            --text-primary:     #EAF2FF;
            --text-secondary:   #8FA3C4;
            --text-muted:       #4C5B7A;
            --font-family:      'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-heading:     'Orbitron', 'Space Grotesk', sans-serif;
            --font-mono:        'JetBrains Mono', 'Fira Code', monospace;
        }

        /* ===== Keyframe Animations ===== */
        @keyframes fx-fade-up {
            from { opacity: 0; transform: translateY(14px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes fx-pulse-glow {
            0%, 100% { box-shadow: 0 0 0 0 rgba(0, 229, 255, 0.35); }
            50%      { box-shadow: 0 0 0 8px rgba(0, 229, 255, 0); }
        }
        @keyframes fx-pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50%      { opacity: 0.45; transform: scale(0.8); }
        }
        @keyframes fx-border-flow {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes fx-shimmer {
            0%   { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        @keyframes fx-spin {
            from { transform: rotate(0deg); }
            to   { transform: rotate(360deg); }
        }
        @keyframes fx-float {
            0%, 100% { transform: translateY(0); }
            50%      { transform: translateY(-6px); }
        }
        @keyframes fx-scan {
            0%   { transform: translateY(-100%); }
            100% { transform: translateY(100%); }
        }

        /* ===== Global Overrides ===== */
        html, body, .stApp {
            background: var(--bg-primary) !important;
            font-family: var(--font-family);
            color: var(--text-primary);
        }
        .stApp {
            background-image:
                linear-gradient(rgba(0, 229, 255, 0.045) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 229, 255, 0.045) 1px, transparent 1px),
                radial-gradient(circle at 15% 10%, rgba(41, 121, 255, 0.10), transparent 45%),
                radial-gradient(circle at 85% 90%, rgba(168, 85, 247, 0.10), transparent 45%);
            background-size: 42px 42px, 42px 42px, cover, cover;
            background-attachment: fixed;
        }
        .block-container {
            padding-top: 1.6rem !important;
            max-width: 1400px;
        }

        /* ===== Hide Streamlit Defaults ===== */
        #MainMenu,
        footer{
            visibility:hidden;
        }
        .stDeployButton { display: none; }

        /* ===== Scrollbar ===== */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-terminal); }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(var(--accent-cyan), var(--accent-purple));
            border-radius: 8px;
        }

        /* ===== Sidebar ===== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #060A18 0%, #0A1226 100%);
            border-right: 1px solid var(--border-color);
            box-shadow: 4px 0 24px rgba(0, 229, 255, 0.05);
        }
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {
            color: var(--text-primary);
            font-family: var(--font-heading);
        }

        /* ===== Input Fields ===== */
        .stTextInput > div > div > input,
        .stDateInput > div > div > input {
            background-color: rgba(5, 9, 24, 0.85) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
            font-family: var(--font-family) !important;
            font-size: 0.9rem !important;
            padding: 0.65rem 1rem !important;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .stTextInput > div > div > input:focus,
        .stDateInput > div > div > input:focus {
            border-color: var(--accent-cyan) !important;
            box-shadow: 0 0 0 3px rgba(0, 229, 255, 0.15) !important;
        }
        .stTextInput label, .stDateInput label {
            color: var(--text-secondary) !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            font-family: var(--font-mono) !important;
        }

        /* ===== Buttons ===== */
        .stButton > button, .stDownloadButton > button {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan)) !important;
            color: #04121A !important;
            border: none !important;
            border-radius: 10px !important;
            font-family: var(--font-heading) !important;
            font-weight: 700 !important;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            font-size: 0.82rem !important;
            padding: 0.7rem 1.1rem !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
            box-shadow: 0 0 18px rgba(0, 229, 255, 0.25);
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 28px rgba(0, 229, 255, 0.45);
            filter: brightness(1.08);
        }
        .stButton > button:active, .stDownloadButton > button:active {
            transform: translateY(0);
        }

        /* ===== File Uploader ===== */
        [data-testid="stFileUploaderDropzone"] {
            background: rgba(10, 15, 36, 0.55) !important;
            border: 1.5px dashed rgba(0, 229, 255, 0.35) !important;
            border-radius: 14px !important;
            transition: border-color 0.25s ease, background 0.25s ease;
        }
        [data-testid="stFileUploaderDropzone"]:hover {
            border-color: var(--accent-cyan) !important;
            background: rgba(0, 229, 255, 0.05) !important;
        }

        /* ===== Alerts ===== */
        .stAlert {
            background: rgba(14, 20, 40, 0.75) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px !important;
            font-family: var(--font-family);
        }

        /* ===== Sidebar Brand ===== */
        .sidebar-brand {
            text-align: center;
            padding: 1.2rem 0 1.4rem;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 1.2rem;
            animation: fx-fade-up 0.5s ease both;
        }
        .brand-logo {
            font-size: 2.4rem;
            filter: drop-shadow(0 0 12px rgba(0, 229, 255, 0.6));
            animation: fx-float 3.5s ease-in-out infinite;
        }
        .brand-name {
            font-family: var(--font-heading);
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 0.4rem;
        }
        .brand-tagline {
            font-size: 0.7rem;
            color: var(--text-muted);
            font-family: var(--font-mono);
            letter-spacing: 0.03em;
            margin-top: 0.2rem;
        }

        /* ===== Sidebar Section Label ===== */
        .sidebar-section {
            font-family: var(--font-mono);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--accent-cyan);
            margin: 1.1rem 0 0.6rem;
            padding-left: 0.1rem;
            border-left: 2px solid var(--accent-cyan);
            padding-left: 0.5rem;
        }

        /* ===== Case Info Card ===== */
        .case-info-card {
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.7rem;
            animation: fx-fade-up 0.4s ease both;
        }
        .ci-row {
            display: flex;
            justify-content: space-between;
            padding: 0.3rem 0;
            border-bottom: 1px dashed rgba(255,255,255,0.06);
            font-size: 0.82rem;
        }
        .ci-row:last-child { border-bottom: none; }
        .ci-label {
            color: var(--text-muted);
            font-family: var(--font-mono);
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .ci-value {
            color: var(--text-primary);
            font-weight: 600;
        }

        /* ===== Status Badge ===== */
        .status-badge {
            display: inline-flex;
            align-items: center;
            font-family: var(--font-mono);
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            padding: 0.28rem 0.7rem;
            border-radius: 999px;
            border: 1px solid var(--border-color);
            background: rgba(255,255,255,0.03);
            color: var(--text-secondary);
        }
        .status-badge.active {
            color: var(--accent-emerald);
            border-color: rgba(34, 197, 94, 0.4);
            background: rgba(34, 197, 94, 0.08);
            animation: fx-pulse-glow 2.4s ease-in-out infinite;
        }
        .status-badge.pending {
            color: var(--accent-amber);
            border-color: rgba(250, 204, 21, 0.4);
            background: rgba(250, 204, 21, 0.08);
        }

        /* ===== Sidebar Footer ===== */
        .sidebar-footer {
            text-align: center;
            padding: 0.75rem 0;
        }
        .sidebar-footer p {
            color: var(--text-muted);
            font-size: 0.65rem;
            font-family: var(--font-mono);
            margin: 0;
            line-height: 1.6;
        }

        /* ===== Hero Section ===== */
        .hero-wrapper {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            background: var(--bg-card);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border: 1px solid var(--border-color);
            border-radius: 18px;
            padding: 1.8rem 2rem;
            position: relative;
            overflow: hidden;
            animation: fx-fade-up 0.5s ease both;
        }
        .hero-wrapper::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(120deg, transparent, rgba(0, 229, 255, 0.08), transparent);
            background-size: 200% 200%;
            animation: fx-border-flow 6s ease infinite;
            pointer-events: none;
        }
        .hero-content { position: relative; z-index: 1; }
        .hero-title {
            font-family: var(--font-heading);
            font-size: 2.3rem;
            font-weight: 900;
            letter-spacing: 0.03em;
            background: linear-gradient(90deg, #EAF2FF, var(--accent-cyan) 45%, var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(0, 229, 255, 0.25);
        }
        .hero-subtitle {
            font-family: var(--font-mono);
            font-size: 0.95rem;
            color: var(--accent-cyan);
            letter-spacing: 0.04em;
            margin-top: 0.3rem;
        }
        .hero-description {
            color: var(--text-secondary);
            font-size: 0.9rem;
            max-width: 640px;
            margin-top: 0.6rem;
            line-height: 1.55;
        }
        .system-status {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: var(--font-mono);
            font-size: 0.78rem;
            color: var(--accent-emerald);
            border: 1px solid rgba(34, 197, 94, 0.35);
            background: rgba(34, 197, 94, 0.08);
            padding: 0.5rem 1rem;
            border-radius: 999px;
            white-space: nowrap;
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-emerald);
            box-shadow: 0 0 8px var(--accent-emerald);
            animation: fx-pulse-dot 1.6s ease-in-out infinite;
        }
        .glow-divider {
            height: 1px;
            margin: 1.6rem 0;
            background: linear-gradient(90deg, transparent, var(--accent-cyan), var(--accent-purple), transparent);
            opacity: 0.5;
        }

        /* ===== Section Header ===== */
        .section-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: var(--font-heading);
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            color: var(--text-primary);
            margin: 0.4rem 0 1rem;
            text-transform: uppercase;
        }
        .sh-icon {
            font-size: 1.1rem;
            filter: drop-shadow(0 0 6px rgba(0, 229, 255, 0.5));
        }

        /* ===== Upload Zone Hint ===== */
        .upload-zone-hint {
            text-align: center;
            padding: 1.6rem 1rem;
            border: 1.5px dashed rgba(0, 229, 255, 0.3);
            border-radius: 14px;
            background: rgba(10, 15, 36, 0.4);
            margin-bottom: 0.8rem;
            transition: border-color 0.3s ease;
        }
        .upload-zone-hint:hover {
            border-color: var(--accent-cyan);
        }
        .uz-icon {
            font-size: 2rem;
            animation: fx-float 3s ease-in-out infinite;
        }
        .uz-title {
            font-family: var(--font-heading);
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-top: 0.5rem;
        }
        .uz-or {
            color: var(--text-muted);
            font-size: 0.75rem;
            margin: 0.3rem 0;
            font-family: var(--font-mono);
        }
        .uz-browse {
            color: var(--accent-cyan);
            font-weight: 600;
            font-size: 0.85rem;
        }
        .uz-formats {
            color: var(--text-muted);
            font-size: 0.72rem;
            font-family: var(--font-mono);
            margin-top: 0.6rem;
        }

        /* ===== File Card ===== */
        .file-card {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            background: var(--bg-card);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 0.7rem 1rem;
            margin-bottom: 0.5rem;
            transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
            animation: fx-fade-up 0.35s ease both;
        }
        .file-card:hover {
            transform: translateX(4px);
            border-color: var(--accent-cyan);
            background: var(--bg-card-hover);
        }
        .fc-icon { font-size: 1.4rem; }
        .fc-info { flex: 1; min-width: 0; }
        .fc-name {
            font-weight: 600;
            font-size: 0.88rem;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .fc-meta {
            font-size: 0.72rem;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }
        .fc-status {
            font-family: var(--font-mono);
            font-size: 0.72rem;
            color: var(--accent-emerald);
            white-space: nowrap;
        }

        /* ===== Progress ===== */
        .progress-label {
            display: flex;
            justify-content: space-between;
            font-family: var(--font-mono);
            font-size: 0.78rem;
            margin-bottom: 0.4rem;
        }
        .pl-text { color: var(--text-secondary); }
        .pl-pct { color: var(--accent-cyan); font-weight: 700; }
        .progress-container {
            width: 100%;
            height: 10px;
            border-radius: 999px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border-color);
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan), var(--accent-purple));
            background-size: 200% 100%;
            animation: fx-shimmer 2.5s linear infinite;
            transition: width 0.6s ease;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
        }

        /* ===== Metric Cards ===== */
        .metric-card {
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.1rem 1.2rem;
            position: relative;
            overflow: hidden;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            animation: fx-fade-up 0.4s ease both;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-cyan);
            box-shadow: 0 10px 30px rgba(0, 229, 255, 0.15);
        }
        .metric-card::after {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, currentColor, transparent);
            opacity: 0.6;
        }
        .metric-card.blue    { color: var(--accent-blue); }
        .metric-card.cyan    { color: var(--accent-cyan); }
        .metric-card.purple  { color: var(--accent-purple); }
        .metric-card.emerald { color: var(--accent-emerald); }
        .metric-card.amber   { color: var(--accent-amber); }
        .metric-card.rose    { color: var(--accent-rose); }
        .metric-icon { font-size: 1.5rem; }
        .metric-value {
            font-family: var(--font-heading);
            font-size: 1.7rem;
            font-weight: 800;
            margin: 0.4rem 0 0.1rem;
            color: var(--text-primary);
        }
        .metric-value.val-green  { color: var(--accent-emerald); }
        .metric-value.val-blue   { color: var(--accent-cyan); }
        .metric-value.val-red    { color: var(--accent-rose); }
        .metric-value.val-yellow { color: var(--accent-amber); }
        .metric-value.val-gray   { color: var(--text-muted); }
        .metric-label {
            font-size: 0.72rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-family: var(--font-mono);
            margin-bottom: 0.5rem;
        }
        .metric-status { margin-top: 0.5rem; }

        /* ===== Activity / Terminal Panel ===== */
        .activity-panel {
            background: var(--bg-terminal);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 0 24px rgba(0, 229, 255, 0.06), inset 0 0 40px rgba(0,0,0,0.4);
        }
        .activity-titlebar {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.6rem 0.9rem;
            background: rgba(255,255,255,0.03);
            border-bottom: 1px solid var(--border-color);
        }
        .dot {
            width: 10px; height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot.red    { background: var(--accent-rose); }
        .dot.yellow { background: var(--accent-amber); }
        .dot.green  { background: var(--accent-emerald); }
        .atb-title {
            margin-left: 0.6rem;
            font-family: var(--font-mono);
            font-size: 0.75rem;
            color: var(--text-muted);
            letter-spacing: 0.04em;
        }
        .activity-body {
            padding: 0.9rem 1rem;
            max-height: 340px;
            overflow-y: auto;
        }
        .activity-log { display: flex; flex-direction: column; gap: 0.5rem; }
        .activity-log .log-line {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            animation: fx-fade-up 0.3s ease both;
        }
        .activity-log .log-time {
            color: var(--text-muted);
            width: 46px;
            flex-shrink: 0;
        }
        .activity-log .log-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .activity-log .log-dot.waiting { background: var(--accent-amber); }
        .activity-log .log-dot.ready   { background: var(--accent-emerald); }
        .activity-log .log-dot.info    { background: var(--accent-blue); }
        .activity-log .log-msg { color: var(--text-secondary); }

        /* ===== Agent Rows ===== */
        .agent-row {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            padding: 0.7rem 0;
            border-bottom: 1px dashed rgba(255,255,255,0.06);
        }
        .agent-row:last-child { border-bottom: none; }
        .agent-row-icon {
            font-size: 1.3rem;
            width: 38px; height: 38px;
            display: flex; align-items: center; justify-content: center;
            border-radius: 10px;
            background: rgba(0, 229, 255, 0.08);
            border: 1px solid var(--border-color);
            flex-shrink: 0;
        }
        .agent-row-icon.agent-pulse-active {
            animation: fx-pulse-glow 1.6s ease-in-out infinite;
            border-color: var(--accent-cyan);
        }
        .agent-row-body { flex: 1; min-width: 0; }
        .agent-row-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.3rem;
        }
        .agent-row-name {
            font-weight: 600;
            font-size: 0.85rem;
            color: var(--text-primary);
        }
        .agent-row-status {
            font-size: 0.74rem;
            color: var(--text-muted);
            font-family: var(--font-mono);
            margin-bottom: 0.4rem;
        }
        .progress-container.agent-progress {
            height: 6px;
        }
        .agent-row-time {
            font-family: var(--font-mono);
            font-size: 0.72rem;
            color: var(--text-muted);
            flex-shrink: 0;
            width: 42px;
            text-align: right;
        }

        /* ===== Result Cards ===== */
        .result-card {
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.2rem 1.3rem;
            margin-bottom: 1rem;
            transition: border-color 0.25s ease, transform 0.25s ease;
            animation: fx-fade-up 0.4s ease both;
        }
        .result-card:hover {
            border-color: var(--accent-cyan);
            transform: translateY(-2px);
        }
        .result-card .rc-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.7rem;
            padding-bottom: 0.6rem;
            border-bottom: 1px solid var(--border-color);
        }
        .result-card .rc-icon {
            font-size: 1.2rem;
            filter: drop-shadow(0 0 6px rgba(0, 229, 255, 0.4));
        }
        .result-card .rc-title {
            font-family: var(--font-heading);
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            color: var(--text-primary);
            margin: 0;
            text-transform: uppercase;
        }
        .result-card .rc-body {
            color: var(--text-secondary);
            font-size: 0.88rem;
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
#  Animated Background FX — grid glow, scanline, floating particles
# ---------------------------------------------------------------------------
def render_background_fx():
    """Inject a fixed, non-interactive animated background layer.

    Purely cosmetic: floating particles + a soft vertical scan glow behind
    all app content. Does not touch any backend, agent, or API logic.
    """

    st.markdown(
        """
        <style>
        #fx-bg-layer {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            overflow: hidden;
        }
        #fx-bg-layer .fx-scanline {
            position: absolute;
            left: 0; right: 0;
            height: 140px;
            background: linear-gradient(180deg, transparent, rgba(0, 229, 255, 0.05), transparent);
            animation: fx-scan 9s linear infinite;
        }
        #fx-bg-layer .fx-particle {
            position: absolute;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(0, 229, 255, 0.9), rgba(0, 229, 255, 0));
            opacity: 0.5;
            animation: fx-particle-drift linear infinite;
        }
        @keyframes fx-particle-drift {
            0%   { transform: translateY(0) translateX(0); opacity: 0; }
            10%  { opacity: 0.6; }
            90%  { opacity: 0.6; }
            100% { transform: translateY(-110vh) translateX(20px); opacity: 0; }
        }
        /* Keep real app content above the fx layer */
        [data-testid="stAppViewContainer"] > .main,
        section[data-testid="stSidebar"] {
            position: relative;
            z-index: 1;
        }
        </style>

        <div id="fx-bg-layer">
            <div class="fx-scanline"></div>
        </div>

        <script>
        (function () {
            const layer = document.getElementById("fx-bg-layer");
            if (!layer || layer.dataset.seeded) return;
            layer.dataset.seeded = "true";
            const colors = ["#00E5FF", "#A855F7", "#2979FF"];
            for (let i = 0; i < 28; i++) {
                const p = document.createElement("div");
                p.className = "fx-particle";
                const size = 2 + Math.random() * 3;
                p.style.width = size + "px";
                p.style.height = size + "px";
                p.style.left = Math.random() * 100 + "vw";
                p.style.top = 100 + Math.random() * 20 + "vh";
                p.style.background = "radial-gradient(circle, " + colors[i % colors.length] + "cc, transparent)";
                p.style.animationDuration = (10 + Math.random() * 14) + "s";
                p.style.animationDelay = (Math.random() * 10) + "s";
                layer.appendChild(p);
            }
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
#  Utility: Format file size
# ---------------------------------------------------------------------------
def format_file_size(size_bytes: int) -> str:
    """Convert a file size in bytes to a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


# ---------------------------------------------------------------------------
#  Utility: Get file icon and type label based on extension
# ---------------------------------------------------------------------------
def get_file_info(filename: str) -> dict:
    """Return an icon and a human-readable type label for a file."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    info_map = {
        "pdf":  {"icon": "📄", "type": "PDF Document"},
        "txt":  {"icon": "📝", "type": "Text File"},
        "png":  {"icon": "🖼️", "type": "PNG Image"},
        "jpg":  {"icon": "📸", "type": "JPEG Image"},
        "jpeg": {"icon": "📸", "type": "JPEG Image"},
    }
    return info_map.get(ext, {"icon": "📁", "type": "Unknown"})


# ---------------------------------------------------------------------------
#  Session State Initialization
# ---------------------------------------------------------------------------
def init_session_state():
    """Initialize Streamlit session state with default values."""
    defaults = {
        "case_name": "",
        "investigator_name": "",
        "investigation_date": date.today(),
        "investigation_started": False,
        "uploaded_files": [],
        "analysis_results": None,
        "analysis_error": None,
        "image_results": [],
        "evidence_results": None,
        "timeline_results": None,
        "report": None,
        "report_pdf_bytes": None,
        "agent_log": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
#  Live Multi-Agent Pipeline Runner
# ---------------------------------------------------------------------------
_AGENT_META = {
    "Document Agent": {"icon": "📄", "verb": "Reading documents…"},
    "Image Agent":    {"icon": "🖼️", "verb": "Analyzing image…"},
    "Evidence Agent": {"icon": "🔗", "verb": "Cross-checking evidence…"},
    "Timeline Agent": {"icon": "🕐", "verb": "Extracting chronology…"},
    "Report Agent":   {"icon": "📝", "verb": "Generating report…"},
}


def _render_agent_panel(placeholder, rows: list[dict]):
    """Render the live agent activity panel into a Streamlit placeholder.

    Each row: {"name": str, "label": str, "state": "pending"|"running"|"done"|"error", "elapsed": float}
    """
    state_meta = {
        "pending": {"dot": "waiting", "badge": "pending", "text": "Queued"},
        "running": {"dot": "waiting", "badge": "pending", "text": "Running"},
        "done":    {"dot": "ready",   "badge": "active",  "text": "Complete"},
        "error":   {"dot": "waiting", "badge": "pending", "text": "Error"},
    }

    cards_html = ""
    for row in rows:
        meta = _AGENT_META.get(row["name"], {"icon": "🤖", "verb": ""})
        sm = state_meta[row["state"]]
        pulse_class = "agent-pulse-active" if row["state"] == "running" else ""
        progress_pct = 100 if row["state"] == "done" else (55 if row["state"] == "running" else 0)
        elapsed_txt = f"{row['elapsed']:.1f}s" if row.get("elapsed") is not None else "—"

        cards_html += f"""
        <div class="agent-row">
            <div class="agent-row-icon {pulse_class}">{meta['icon']}</div>
            <div class="agent-row-body">
                <div class="agent-row-top">
                    <span class="agent-row-name">{row['label']}</span>
                    <span class="status-badge {sm['badge']}">
                        <span class="log-dot {sm['dot']}" style="display:inline-block;margin-right:4px;"></span>{sm['text']}
                    </span>
                </div>
                <div class="agent-row-status">{row.get('detail', meta['verb'])}</div>
                <div class="progress-container agent-progress">
                    <div class="progress-fill" style="width: {progress_pct}%;"></div>
                </div>
            </div>
            <div class="agent-row-time">{elapsed_txt}</div>
        </div>
        """

    placeholder.markdown(
        f"""
        <div class="activity-panel">
            <div class="activity-titlebar">
                <span class="dot red"></span>
                <span class="dot yellow"></span>
                <span class="dot green"></span>
                <span class="atb-title">Live Agent Activity</span>
            </div>
            <div class="activity-body" style="max-height: none;">
                {cards_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run_investigation_pipeline():
    """Run the full multi-agent investigation pipeline with a live status panel."""

    st.session_state.investigation_started = True
    st.session_state.analysis_results = None
    st.session_state.analysis_error = None
    st.session_state.image_results = []
    st.session_state.evidence_results = None
    st.session_state.timeline_results = None
    st.session_state.report = None
    st.session_state.report_pdf_bytes = None

    uploaded = st.session_state.uploaded_files
    image_files = get_image_files(uploaded)

    # Build the initial row list
    rows = [{"name": "Document Agent", "label": "Document Agent — Reading PDF/TXT", "state": "pending", "elapsed": None}]
    for f in image_files:
        rows.append({"name": "Image Agent", "label": f"Image Agent — {f.name}", "state": "pending", "elapsed": None})
    rows.append({"name": "Evidence Agent", "label": "Evidence Agent — Cross-checking evidence", "state": "pending", "elapsed": None})
    rows.append({"name": "Timeline Agent", "label": "Timeline Agent — Building chronology", "state": "pending", "elapsed": None})
    rows.append({"name": "Report Agent", "label": "Report Agent — Compiling report", "state": "pending", "elapsed": None})

    panel = st.sidebar.empty()
    _render_agent_panel(panel, rows)

    # --- 1. Document Agent ---
    doc_row = rows[0]
    doc_row["state"] = "running"
    _render_agent_panel(panel, rows)
    t0 = _time.time()

    document_result = None
    if has_document_files(uploaded):
        combined_text = extract_all_text(uploaded)
        document_result = DocumentAgent().analyze(combined_text)
    else:
        document_result = DocumentAgent()._empty_result("No PDF/TXT files were uploaded.")

    doc_row["elapsed"] = _time.time() - t0
    doc_row["state"] = "error" if document_result.get("status") == "error" else "done"
    doc_row["detail"] = document_result.get("message") or "Document analysis complete."
    _render_agent_panel(panel, rows)

    if document_result.get("status") == "success":
        st.session_state.analysis_results = document_result
    elif document_result.get("status") == "error":
        st.session_state.analysis_error = document_result.get("message", "Unknown error.")

    # --- 2. Image Agent (one per image) ---
    image_agent = ImageAgent()
    image_results = []
    for i, f in enumerate(image_files):
        row = rows[1 + i]
        row["state"] = "running"
        _render_agent_panel(panel, rows)
        t0 = _time.time()

        result = image_agent.analyze(read_image_bytes(f), filename=f.name)
        image_results.append(result)

        row["elapsed"] = _time.time() - t0
        row["state"] = "error" if result.get("status") == "error" else "done"
        row["detail"] = result.get("scene_summary") or result.get("message") or "Image analysis complete."
        _render_agent_panel(panel, rows)

    st.session_state.image_results = image_results

    # --- 3. Evidence Agent ---
    ev_row = rows[1 + len(image_files)]
    ev_row["state"] = "running"
    _render_agent_panel(panel, rows)
    t0 = _time.time()

    evidence_result = EvidenceAgent().process(document_result, image_results)

    ev_row["elapsed"] = _time.time() - t0
    ev_row["state"] = "done"
    ev_row["detail"] = f"Risk level: {evidence_result.get('risk_level', 'low').upper()}"
    _render_agent_panel(panel, rows)
    st.session_state.evidence_results = evidence_result

    # --- 4. Timeline Agent ---
    tl_row = rows[2 + len(image_files)]
    tl_row["state"] = "running"
    _render_agent_panel(panel, rows)
    t0 = _time.time()

    timeline_result = TimelineAgent().process(document_result, image_results)

    tl_row["elapsed"] = _time.time() - t0
    tl_row["state"] = "done"
    tl_row["detail"] = f"{timeline_result.get('total_events', 0)} events sequenced"
    _render_agent_panel(panel, rows)
    st.session_state.timeline_results = timeline_result

    # --- 5. Report Agent ---
    rp_row = rows[3 + len(image_files)]
    rp_row["state"] = "running"
    _render_agent_panel(panel, rows)
    t0 = _time.time()

    report_agent = ReportAgent()
    report = report_agent.process(
        case_name=st.session_state.case_name,
        investigator_name=st.session_state.investigator_name,
        investigation_date=st.session_state.investigation_date,
        document_result=document_result,
        image_results=image_results,
        evidence_result=evidence_result,
        timeline_result=timeline_result,
    )
    try:
        pdf_bytes = report_agent.build_pdf(report)
        st.session_state.report_pdf_bytes = pdf_bytes
    except Exception:
        st.session_state.report_pdf_bytes = None

    rp_row["elapsed"] = _time.time() - t0
    rp_row["state"] = "done"
    rp_row["detail"] = "Report ready for export."
    _render_agent_panel(panel, rows)
    st.session_state.report = report

    if document_result.get("status") == "success":
        st.success("✅ Investigation analysis complete!")
    elif document_result.get("status") == "empty" and not image_results:
        st.warning(f"📭 {document_result.get('message', 'No content found.')}")
    elif st.session_state.analysis_error:
        st.error(f"❌ {st.session_state.analysis_error}")
    else:
        st.success("✅ Image evidence analyzed!")


# ---------------------------------------------------------------------------
#  Sidebar — Case Configuration
# ---------------------------------------------------------------------------
def render_sidebar():
    """Render the sidebar with case creation form and branding."""

    

    with st.sidebar:
        
        # -- Branding: Investigation-styled logo --
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-logo">🛡️</div>
                <div class="brand-name">CaseMind AI</div>
                <div class="brand-tagline">Multi-Agent Investigation Assistant</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -- New Case Section --
        st.markdown(
            '<div class="sidebar-section">📁 Create New Case</div>',
            unsafe_allow_html=True,
        )

        # Case Name input
        case_name = st.text_input(
            "Case Name",
            value=st.session_state.case_name,
            placeholder="e.g. Operation Nightfall",
        )
        st.session_state.case_name = case_name

        # Investigator Name input
        investigator_name = st.text_input(
            "Investigator Name",
            value=st.session_state.investigator_name,
            placeholder="e.g. Detective Smith",
        )
        st.session_state.investigator_name = investigator_name

        # Investigation Date input
        investigation_date = st.date_input(
            "Investigation Date",
            value=st.session_state.investigation_date,
        )
        st.session_state.investigation_date = investigation_date

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # Analyze Evidence button — large, premium gradient
        if st.button("🧠  Analyze Evidence", use_container_width=True):
            if not case_name or not investigator_name:
                st.warning("⚠️ Please fill in Case Name and Investigator Name.")
            elif not st.session_state.uploaded_files:
                st.warning("⚠️ Please upload at least one evidence file.")
            elif not has_document_files(st.session_state.uploaded_files) and not has_image_files(st.session_state.uploaded_files):
                st.warning("⚠️ Please upload at least one PDF, TXT, PNG, or JPG file for analysis.")
            elif not is_groq_configured():
                st.error("🔑 Groq API key is not configured. Please set GROQ_API_KEY in your .env file.")
            else:
                run_investigation_pipeline()

        # -- Export Report button --
        if st.session_state.get("report"):
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.session_state.get("report_pdf_bytes"):
                st.download_button(
                    "📤  Export Report (PDF)",
                    data=st.session_state.report_pdf_bytes,
                    file_name=f"{(case_name or 'CaseMind').replace(' ', '_')}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

        # -- Active Case Info (shown when investigation is started) --
        if st.session_state.investigation_started:
            st.markdown(
                '<div class="sidebar-section">📋 Active Case</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="case-info-card">
                    <div class="ci-row">
                        <span class="ci-label">Case</span>
                        <span class="ci-value">{st.session_state.case_name}</span>
                    </div>
                    <div class="ci-row">
                        <span class="ci-label">Lead</span>
                        <span class="ci-value">{st.session_state.investigator_name}</span>
                    </div>
                    <div class="ci-row">
                        <span class="ci-label">Date</span>
                        <span class="ci-value">{st.session_state.investigation_date.strftime('%b %d, %Y')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                '<span class="status-badge active">● Investigation Active</span>',
                unsafe_allow_html=True,
            )

        # -- Footer --
        st.markdown("---")
        st.markdown(
            """
            <div class="sidebar-footer">
                <p>
                    Built for College Competition<br>
                    © 2026 CaseMind AI
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
#  Hero Section — Home Page Header
# ---------------------------------------------------------------------------
def render_hero():
    """Render the hero section with title, subtitle, description and status badge."""

    st.markdown(
        """
        <div class="hero-wrapper">
            <div class="hero-content">
                <div class="hero-title">CaseMind AI</div>
                <div class="hero-subtitle">Multi-Agent Investigation Assistant</div>
                <div class="hero-description">
                    Analyze documents, chats, and images using specialized AI agents
                    that collaborate to generate investigation insights.
                </div>
            </div>
            <div class="system-status">
                <span class="pulse-dot"></span>
                AI System Ready
            </div>
        </div>
        <div class="glow-divider"></div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
#  Upload Section
# ---------------------------------------------------------------------------
def render_upload_section():
    """Render the evidence upload section with descriptive zone and file cards."""

    st.markdown(
        '<div class="section-header"><span class="sh-icon">📎</span> Upload Evidence</div>',
        unsafe_allow_html=True,
    )

    # Upload zone hint card
    st.markdown(
        """
        <div class="upload-zone-hint">
            <div class="uz-icon">📂</div>
            <div class="uz-title">Drop evidence files here</div>
            <div class="uz-or">or</div>
            <div class="uz-browse">Click to browse</div>
            <div class="uz-formats">Supported formats: PDF • TXT • PNG • JPG • JPEG</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Multi-file uploader — the native Streamlit widget
    uploaded_files = st.file_uploader(
        "Upload evidence files",
        type=["pdf", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    # Display uploaded file cards with icon, name, type, and status
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

        st.markdown(
            f"""
            <div style="margin: 0.75rem 0;">
                <span class="status-badge active">
                    ● {len(uploaded_files)} file{'s' if len(uploaded_files) != 1 else ''} uploaded
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for f in uploaded_files:
            info = get_file_info(f.name)
            size = format_file_size(f.size)
            st.markdown(
                f"""
                <div class="file-card">
                    <span class="fc-icon">{info['icon']}</span>
                    <div class="fc-info">
                        <div class="fc-name">{f.name}</div>
                        <div class="fc-meta">{info['type']} • {size}</div>
                    </div>
                    <div class="fc-status">
                        <span>✓</span> Uploaded
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.session_state.uploaded_files = []

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
#  Investigation Progress
# ---------------------------------------------------------------------------
def render_progress():
    """Render the investigation progress bar — dynamic based on analysis state."""

    st.markdown(
        '<div class="section-header"><span class="sh-icon">⏳</span> Investigation Progress</div>',
        unsafe_allow_html=True,
    )

    # Progress percentage — derived from how many pipeline stages have completed
    if st.session_state.get("report"):
        progress_pct = 100
    elif st.session_state.get("timeline_results"):
        progress_pct = 85
    elif st.session_state.get("evidence_results"):
        progress_pct = 65
    elif st.session_state.get("image_results") or st.session_state.get("analysis_results"):
        progress_pct = 40
    elif st.session_state.get("investigation_started"):
        progress_pct = 15
    else:
        progress_pct = 0

    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <div class="progress-label">
                <span class="pl-text">Overall investigation completion</span>
                <span class="pl-pct">{progress_pct}%</span>
            </div>
            <div class="progress-container">
                <div class="progress-fill" style="width: {progress_pct}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
#  Dashboard — Metric Cards
# ---------------------------------------------------------------------------
def _compute_dashboard_metrics() -> list[dict]:
    """Compute live dashboard metric values from session state."""
    results = st.session_state.get("analysis_results")
    image_results = st.session_state.get("image_results", []) or []
    evidence = st.session_state.get("evidence_results")
    timeline = st.session_state.get("timeline_results")
    uploaded = st.session_state.get("uploaded_files", [])
    has_results = results is not None or bool(image_results)

    # Count document files (PDF/TXT) vs image files
    doc_count = sum(
        1 for f in uploaded
        if f.name.rsplit(".", 1)[-1].lower() in {"pdf", "txt"}
    )
    img_uploaded_count = sum(
        1 for f in uploaded
        if f.name.rsplit(".", 1)[-1].lower() in {"png", "jpg", "jpeg"}
    )
    img_analyzed_count = sum(1 for r in image_results if r.get("status") == "success")
    event_count = timeline.get("total_events", 0) if timeline else 0
    contradiction_count = len((evidence or {}).get("contradictions", []) or []) if evidence else (
        len(results.get("contradictions", [])) if results else 0
    )
    confidence = results.get("confidence_score", 0) if results else 0
    risk_score = evidence.get("risk_score", 0) if evidence else 0
    risk_level = evidence.get("risk_level", "low") if evidence else "low"

    def _status(val, is_done=False):
        if is_done:
            return {"val_class": "val-green", "status_text": "Complete", "status_class": "active"}
        if val and val != "0" and val != "—":
            return {"val_class": "val-blue", "status_text": "Active", "status_class": "active"}
        return {"val_class": "val-gray", "status_text": "Pending", "status_class": "pending"}

    risk_color_map = {"low": "val-green", "medium": "val-yellow", "high": "val-red"}

    return [
        {
            "icon": "📄",
            "value": str(doc_count),
            "label": "Documents",
            "color": "blue",
            **_status(doc_count, results is not None),
        },
        {
            "icon": "🖼️",
            "value": f"{img_analyzed_count}/{img_uploaded_count}" if img_uploaded_count else "0",
            "label": "Images Analyzed",
            "color": "purple",
            **_status(img_uploaded_count, img_analyzed_count > 0 and img_analyzed_count == img_uploaded_count),
        },
        {
            "icon": "🕐",
            "value": str(event_count) if event_count else "—",
            "label": "Timeline Events",
            "color": "emerald",
            **_status(event_count, event_count > 0),
        },
        {
            "icon": "⚠️",
            "value": str(contradiction_count) if contradiction_count else "0",
            "label": "Contradictions",
            "color": "rose",
            **({"val_class": "val-red", "status_text": "Found", "status_class": "active"}
               if contradiction_count > 0
               else _status(0, has_results)),
        },
        {
            "icon": "🔗",
            "value": str(len(uploaded)) if uploaded else "0",
            "label": "Evidence Files",
            "color": "amber",
            **_status(len(uploaded), has_results),
        },
        {
            "icon": "📋",
            "value": f"{confidence}%" if results else "—",
            "label": "AI Confidence",
            "color": "cyan",
            **_status(confidence, results is not None),
        },
        {
            "icon": "🚨",
            "value": f"{risk_score}" if evidence else "—",
            "label": f"Risk Score ({risk_level.upper()})" if evidence else "Risk Score",
            "color": "rose" if risk_level == "high" else ("amber" if risk_level == "medium" else "emerald"),
            "val_class": risk_color_map.get(risk_level, "val-gray") if evidence else "val-gray",
            "status_text": risk_level.capitalize() if evidence else "Pending",
            "status_class": "active" if evidence else "pending",
        },
        {
            "icon": "📊",
            "value": f"{event_count + contradiction_count}" if has_results else "—",
            "label": "Total Findings",
            "color": "blue",
            **_status(event_count + contradiction_count, has_results),
        },
    ]


def render_dashboard():
    """Render the investigation dashboard with live metric cards."""

    st.markdown(
        '<div class="section-header"><span class="sh-icon">📊</span> Investigation Dashboard</div>',
        unsafe_allow_html=True,
    )

    metrics = _compute_dashboard_metrics()

    # Render cards in an 8-column grid
    cols = st.columns(8)
    for i, m in enumerate(metrics):
        with cols[i]:
            st.markdown(
                f"""
                <div class="metric-card {m['color']}">
                    <div class="metric-icon">{m['icon']}</div>
                    <div class="metric-value {m['val_class']}">{m['value']}</div>
                    <div class="metric-label">{m['label']}</div>
                    <div class="metric-status">
                        <span class="status-badge {m['status_class']}">{m['status_text']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
#  Live AI Activity Panel
# ---------------------------------------------------------------------------
def render_activity_panel():
    """Render the investigation activity panel — real results if a run has occurred."""

    st.markdown(
        '<div class="section-header"><span class="sh-icon">📡</span> Live Investigation Activity</div>',
        unsafe_allow_html=True,
    )

    now = datetime.now()
    doc_result = st.session_state.get("analysis_results")
    image_results = st.session_state.get("image_results", []) or []
    evidence = st.session_state.get("evidence_results")
    timeline = st.session_state.get("timeline_results")
    report = st.session_state.get("report")

    if not st.session_state.get("investigation_started"):
        t1 = now.strftime("%H:%M:%S")
        t2 = (now.replace(second=max(now.second - 2, 0))).strftime("%H:%M:%S")
        t3 = (now.replace(second=max(now.second - 5, 0))).strftime("%H:%M:%S")
        log_lines = f"""
            <div class="log-line">
                <span class="log-time">{t3}</span>
                <span class="log-dot ready"></span>
                <span class="log-msg">System initialized — all agents on standby</span>
            </div>
            <div class="log-line">
                <span class="log-time">{t2}</span>
                <span class="log-dot info"></span>
                <span class="log-msg">Document Agent ready • Image Agent ready • Evidence Agent ready • Timeline Agent ready • Report Agent ready</span>
            </div>
            <div class="log-line">
                <span class="log-time">{t1}</span>
                <span class="log-dot waiting"></span>
                <span class="log-msg">Waiting to start investigation…</span>
            </div>
        """
    else:
        t = now.strftime("%H:%M:%S")
        lines = []
        if doc_result is not None:
            lines.append(("ready", f"Document Agent — {doc_result.get('status', 'unknown').upper()}: "
                                    f"{len(doc_result.get('events', []))} events, "
                                    f"{len(doc_result.get('people', []))} people identified"))
        for img in image_results:
            status_txt = "found evidence" if img.get("status") == "success" else img.get("message", "failed")
            lines.append(("ready" if img.get("status") == "success" else "waiting",
                           f"Image Agent — {img.get('file')}: {status_txt}"))
        if evidence is not None:
            lines.append(("ready", f"Evidence Agent — merged {evidence.get('documents_analyzed', 0)} document(s) "
                                    f"and {evidence.get('images_analyzed', 0)} image(s), risk level "
                                    f"{evidence.get('risk_level', 'low').upper()}"))
        if timeline is not None:
            lines.append(("ready", f"Timeline Agent — sequenced {timeline.get('total_events', 0)} events"))
        if report is not None:
            lines.append(("info", "Report Agent — investigation report compiled and ready for export"))

        log_lines = "".join(
            f"""<div class="log-line">
                    <span class="log-time">{t}</span>
                    <span class="log-dot {dot}"></span>
                    <span class="log-msg">{msg}</span>
                </div>"""
            for dot, msg in lines
        )

    st.markdown(
        f"""
        <div class="activity-panel">
            <div class="activity-titlebar">
                <span class="dot red"></span>
                <span class="dot yellow"></span>
                <span class="dot green"></span>
                <span class="atb-title">Agent Activity Log</span>
            </div>
            <div class="activity-body">
                <div class="activity-log">
                    {log_lines}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
#  Investigation Results — Placeholder Sections
# ---------------------------------------------------------------------------
def _render_placeholder_results():
    """Render the default placeholder cards when no analysis has been run."""

    # --- Timeline ---
    st.markdown(
        """
        <div class="result-card">
            <div class="rc-header">
                <span class="rc-icon">🕐</span>
                <h3 class="rc-title">Timeline</h3>
            </div>
            <p class="rc-body">
                No timeline has been generated yet. Upload evidence and start
                analysis to automatically reconstruct a chronological sequence
                of events from all submitted documents and images.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="result-card">
                <div class="rc-header">
                    <span class="rc-icon">👤</span>
                    <h3 class="rc-title">Important People</h3>
                </div>
                <p class="rc-body">
                    No key individuals have been identified yet. The AI agents
                    will extract and profile important people mentioned across
                    all evidence sources, including relationships and roles.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="result-card">
                <div class="rc-header">
                    <span class="rc-icon">⚠️</span>
                    <h3 class="rc-title">Contradictions</h3>
                </div>
                <p class="rc-body">
                    No contradictions detected yet. The Evidence Agent will
                    cross-reference all sources to identify inconsistencies,
                    conflicting statements, and factual discrepancies.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="result-card">
            <div class="rc-header">
                <span class="rc-icon">📝</span>
                <h3 class="rc-title">Summary</h3>
            </div>
            <p class="rc-body">
                No investigation summary is available yet. Once evidence is
                analyzed, a comprehensive summary will be generated covering
                all findings, key events, identified patterns, and the
                overall assessment of the case.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="result-card">
            <div class="rc-header">
                <span class="rc-icon">💡</span>
                <h3 class="rc-title">Recommendations</h3>
            </div>
            <p class="rc-body">
                No recommendations have been generated yet. After analysis,
                the Report Agent will suggest prioritized next steps, areas
                requiring further investigation, and potential leads to pursue.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_live_results(results: dict):
    """Render investigation results populated from Groq AI analysis."""

    # --- Timeline (prefer the merged Timeline Agent output, source-tagged) ---
    timeline_result = st.session_state.get("timeline_results")
    merged_timeline = timeline_result.get("timeline", []) if timeline_result else []

    if merged_timeline:
        timeline_html_items = ""
        for entry in merged_timeline:
            timeline_html_items += (
                f'<div style="margin-bottom: 0.6rem; padding-left: 1rem; '
                f'border-left: 2px solid var(--accent-cyan);">'
                f'<span style="color: var(--accent-cyan); font-weight: 600; '
                f'font-size: 0.82rem;">{entry.get("time", "Unknown date")}</span> '
                f'<span style="color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase; '
                f'letter-spacing: 0.04em;">— {entry.get("source", "")} · {entry.get("confidence", 0)}% conf.</span><br>'
                f'<span style="color: var(--text-secondary); font-size: 0.88rem;">{entry.get("event", "")}</span>'
                f'</div>'
            )
        timeline_body = timeline_html_items
    else:
        dates = results.get("dates_times", [])
        events = results.get("events", [])
        if dates or events:
            max_len = max(len(dates), len(events))
            timeline_html_items = ""
            for i in range(max_len):
                dt = dates[i] if i < len(dates) else "Unknown date"
                ev = events[i] if i < len(events) else "No description"
                timeline_html_items += (
                    f'<div style="margin-bottom: 0.6rem; padding-left: 1rem; '
                    f'border-left: 2px solid var(--accent-cyan);">'
                    f'<span style="color: var(--accent-cyan); font-weight: 600; '
                    f'font-size: 0.82rem;">{dt}</span><br>'
                    f'<span style="color: var(--text-secondary); font-size: 0.88rem;">{ev}</span>'
                    f'</div>'
                )
            timeline_body = timeline_html_items
        else:
            timeline_body = (
                '<p class="rc-body">No timeline events were identified in the evidence.</p>'
            )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="rc-header">
                <span class="rc-icon">🕐</span>
                <h3 class="rc-title">Timeline</h3>
            </div>
            {timeline_body}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Two-column layout
    col1, col2 = st.columns(2)

    with col1:
        # --- Important People ---
        people = results.get("people", [])
        if people:
            people_html = ""
            for p in people:
                name = p.get("name", "Unknown") if isinstance(p, dict) else str(p)
                role = p.get("role", "Not specified") if isinstance(p, dict) else "Not specified"
                people_html += (
                    f'<div style="margin-bottom: 0.5rem;">'
                    f'<span style="color: var(--text-primary); font-weight: 600; '
                    f'font-size: 0.9rem;">• {name}</span><br>'
                    f'<span style="color: var(--text-muted); font-size: 0.8rem; '
                    f'padding-left: 0.85rem;">{role}</span></div>'
                )
            people_body = people_html
        else:
            people_body = '<p class="rc-body">No key individuals were identified in the evidence.</p>'

        st.markdown(
            f"""
            <div class="result-card">
                <div class="rc-header">
                    <span class="rc-icon">👤</span>
                    <h3 class="rc-title">Important People</h3>
                </div>
                {people_body}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        # --- Contradictions (+ cross-source flags from the Evidence Agent) ---
        contradictions = list(results.get("contradictions", []))
        evidence_results = st.session_state.get("evidence_results")
        cross_notes = evidence_results.get("cross_reference_notes", []) if evidence_results else []

        if contradictions or cross_notes:
            contra_html = ""
            for c in contradictions:
                contra_html += (
                    f'<div style="margin-bottom: 0.45rem; color: var(--text-secondary); '
                    f'font-size: 0.88rem;">'
                    f'<span style="color: var(--accent-rose);">⚠</span> {c}</div>'
                )
            for c in cross_notes:
                contra_html += (
                    f'<div style="margin-bottom: 0.45rem; color: var(--text-secondary); '
                    f'font-size: 0.88rem;">'
                    f'<span style="color: var(--accent-cyan);">🔗</span> {c}</div>'
                )
            contra_body = contra_html
        else:
            contra_body = (
                '<p class="rc-body">No contradictions or inconsistencies were '
                'detected in the evidence.</p>'
            )

        st.markdown(
            f"""
            <div class="result-card">
                <div class="rc-header">
                    <span class="rc-icon">⚠️</span>
                    <h3 class="rc-title">Contradictions</h3>
                </div>
                {contra_body}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Summary ---
    summary = results.get("summary", "")
    summary_body = (
        f'<p class="rc-body">{summary}</p>'
        if summary
        else '<p class="rc-body">No summary could be generated from the evidence.</p>'
    )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="rc-header">
                <span class="rc-icon">📝</span>
                <h3 class="rc-title">Summary</h3>
            </div>
            {summary_body}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Recommendations ---
    recommendations = results.get("recommendations", [])
    if recommendations:
        rec_html = ""
        for idx, r in enumerate(recommendations, 1):
            rec_html += (
                f'<div style="margin-bottom: 0.45rem; color: var(--text-secondary); '
                f'font-size: 0.88rem;">'
                f'<span style="color: var(--accent-amber); font-weight: 600;">{idx}.</span> {r}</div>'
            )
        rec_body = rec_html
    else:
        rec_body = (
            '<p class="rc-body">No recommendations were generated from the evidence.</p>'
        )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="rc-header">
                <span class="rc-icon">💡</span>
                <h3 class="rc-title">Recommendations</h3>
            </div>
            {rec_body}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_image_analysis_results():
    """Render a beautifully formatted card for each analyzed image."""

    image_results = st.session_state.get("image_results", []) or []
    if not image_results:
        return

    st.markdown(
        '<div class="section-header"><span class="sh-icon">🖼️</span> Image Analysis</div>',
        unsafe_allow_html=True,
    )

    risk_badge = {"low": "active", "medium": "pending", "high": "pending"}
    risk_color = {"low": "var(--accent-emerald)", "medium": "var(--accent-amber)", "high": "var(--accent-rose)"}

    for img in image_results:
        if img.get("status") != "success":
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="rc-header">
                        <span class="rc-icon">❌</span>
                        <h3 class="rc-title">{img.get('file', 'Image')}</h3>
                    </div>
                    <p class="rc-body" style="color: var(--accent-rose);">{img.get('message', 'Analysis failed.')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            continue

        def _tags(items, color="var(--accent-blue)"):
            if not items:
                return '<span style="color: var(--text-muted); font-size: 0.85rem;">None detected</span>'
            return "".join(
                f'<span style="display:inline-block; background: rgba(0,191,255,0.08); '
                f'border: 1px solid rgba(0,191,255,0.25); color: {color}; border-radius: 999px; '
                f'padding: 0.2rem 0.7rem; margin: 0.15rem; font-size: 0.78rem;">{it}</span>'
                for it in items
            )

        risk = img.get("risk_level", "low")
        col_l, col_r = st.columns([1, 1])

        with col_l:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="rc-header">
                        <span class="rc-icon">🖼️</span>
                        <h3 class="rc-title">{img.get('file', 'Image')}</h3>
                        <span class="status-badge {risk_badge.get(risk, 'active')}" style="margin-left:auto; color:{risk_color.get(risk)}; border-color:{risk_color.get(risk)}55;">
                            {risk.upper()} RISK
                        </span>
                    </div>
                    <p class="rc-body" style="margin-bottom: 0.75rem;"><b>Scene:</b> {img.get('scene_summary') or 'No description generated.'}</p>
                    <p class="rc-body" style="font-size:0.8rem; color: var(--text-muted); margin-bottom: 0.25rem; text-transform: uppercase; letter-spacing:0.05em;">People ({img.get('people_count', 0)})</p>
                    <div style="margin-bottom: 0.6rem;">{_tags(img.get('people', []))}</div>
                    <p class="rc-body" style="font-size:0.8rem; color: var(--text-muted); margin-bottom: 0.25rem; text-transform: uppercase; letter-spacing:0.05em;">Objects</p>
                    <div style="margin-bottom: 0.6rem;">{_tags(img.get('objects', []))}</div>
                    <p class="rc-body" style="font-size:0.8rem; color: var(--text-muted); margin-bottom: 0.25rem; text-transform: uppercase; letter-spacing:0.05em;">Vehicles &amp; Weapons</p>
                    <div>{_tags(img.get('vehicles', []) + img.get('weapons', []), color='var(--accent-rose)' if img.get('weapons') else 'var(--accent-blue)')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_r:
            ocr_text = img.get("ocr_text") or "No readable text detected."
            plates = ", ".join(img.get("license_plates", [])) or "None detected"
            dt_visible = img.get("date_time_visible") or "Not visible"
            evidence_list = "".join(f"<li>{e}</li>" for e in img.get("potential_evidence", [])) or "<li>None flagged</li>"
            suspicious_list = "".join(f"<li>{e}</li>" for e in img.get("suspicious_indicators", [])) or "<li>None flagged</li>"

            st.markdown(
                f"""
                <div class="result-card">
                    <div class="rc-header">
                        <span class="rc-icon">🔎</span>
                        <h3 class="rc-title">Forensic Details</h3>
                    </div>
                    <p class="rc-body" style="font-size:0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing:0.05em; margin-bottom:0.25rem;">OCR Text</p>
                    <p class="rc-body" style="font-family: var(--font-mono); font-size: 0.82rem; background: #0D1326; border-radius: 8px; padding: 0.6rem 0.8rem; border: 1px solid var(--border-color);">{ocr_text}</p>
                    <p class="rc-body" style="margin-top:0.6rem;"><b>License Plates:</b> {plates}</p>
                    <p class="rc-body"><b>Date/Time Visible:</b> {dt_visible}</p>
                    <p class="rc-body" style="font-size:0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing:0.05em; margin-top:0.6rem; margin-bottom:0.25rem;">Potential Evidence</p>
                    <ul class="rc-body" style="padding-left: 1.1rem; margin:0;">{evidence_list}</ul>
                    <p class="rc-body" style="font-size:0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing:0.05em; margin-top:0.6rem; margin-bottom:0.25rem;">Suspicious Indicators</p>
                    <ul class="rc-body" style="padding-left: 1.1rem; margin:0;">{suspicious_list}</ul>
                    <p class="rc-body" style="margin-top:0.6rem;"><b>Confidence:</b> {img.get('confidence_score', 0)}%</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)


def render_investigation_graph():
    """Render a lightweight entity-relationship graph from merged evidence."""

    evidence = st.session_state.get("evidence_results")
    if not evidence:
        return

    people = [p["name"] for p in evidence.get("people", [])][:8]
    locations = evidence.get("locations", [])[:6]
    vehicles = evidence.get("vehicles", [])[:6]
    objects_of_interest = (evidence.get("weapons", []) + evidence.get("potential_evidence", []))[:6]

    if not (people or locations or vehicles or objects_of_interest):
        return

    st.markdown(
        '<div class="section-header"><span class="sh-icon">🕸️</span> Investigation Graph</div>',
        unsafe_allow_html=True,
    )

    try:
        import graphviz
        graph = graphviz.Digraph()
        graph.attr(bgcolor="transparent", rankdir="LR")
        graph.attr("node", fontname="Helvetica", fontsize="11", style="filled", color="#1E2A45", fontcolor="#F1F5F9")

        case_label = st.session_state.get("case_name") or "Case"
        graph.node("CASE", case_label, shape="box", fillcolor="#00BFFF33", color="#00BFFF")

        for p in people:
            node_id = f"P_{p}"
            graph.node(node_id, f"👤 {p}", fillcolor="#8B5CF633", color="#8B5CF6")
            graph.edge("CASE", node_id, label="involves", color="#4B5B7A", fontcolor="#94A3B8", fontsize="9")

        for loc in locations:
            node_id = f"L_{loc}"
            graph.node(node_id, f"📍 {loc}", fillcolor="#22C55E33", color="#22C55E")
            graph.edge("CASE", node_id, label="at", color="#4B5B7A", fontcolor="#94A3B8", fontsize="9")

        for v in vehicles:
            node_id = f"V_{v}"
            graph.node(node_id, f"🚗 {v}", fillcolor="#FACC1533", color="#FACC15")
            graph.edge("CASE", node_id, label="seen", color="#4B5B7A", fontcolor="#94A3B8", fontsize="9")

        for o in objects_of_interest:
            node_id = f"O_{o}"
            graph.node(node_id, f"🔎 {o}", fillcolor="#EF444433", color="#EF4444")
            graph.edge("CASE", node_id, label="evidence", color="#4B5B7A", fontcolor="#94A3B8", fontsize="9")

        st.graphviz_chart(graph, use_container_width=True)
    except Exception:
        st.info(
            "Graph rendering requires the `graphviz` system package. "
            "Showing a text summary of connections instead."
        )
        summary_items = (
            [f"👤 {p}" for p in people] + [f"📍 {l}" for l in locations]
            + [f"🚗 {v}" for v in vehicles] + [f"🔎 {o}" for o in objects_of_interest]
        )
        st.markdown(
            "".join(
                f'<span style="display:inline-block; background: rgba(0,191,255,0.08); '
                f'border: 1px solid rgba(0,191,255,0.25); color: var(--accent-blue); border-radius: 999px; '
                f'padding: 0.25rem 0.8rem; margin: 0.2rem; font-size: 0.82rem;">{it}</span>'
                for it in summary_items
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)


def render_investigation_results():
    """Render the investigation results — live data or placeholders."""

    st.markdown(
        '<div class="section-header"><span class="sh-icon">🔍</span> Investigation Results</div>',
        unsafe_allow_html=True,
    )

    results = st.session_state.get("analysis_results")
    error = st.session_state.get("analysis_error")
    has_image_data = any(r.get("status") == "success" for r in st.session_state.get("image_results", []) or [])

    if error and not has_image_data:
        st.markdown(
            f"""
            <div class="result-card">
                <div class="rc-header">
                    <span class="rc-icon">❌</span>
                    <h3 class="rc-title">Analysis Error</h3>
                </div>
                <p class="rc-body" style="color: var(--accent-rose);">{error}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif results or has_image_data:
        _render_live_results(results or {})
    else:
        _render_placeholder_results()


# ---------------------------------------------------------------------------
#  Footer
# ---------------------------------------------------------------------------
def render_footer():
    """Render the application footer."""

    st.markdown(
        """
        <div class="glow-divider"></div>
        <div style="text-align: center; padding: 1.25rem 0 2.5rem 0;">
            <p style="color: var(--text-muted); font-size: 0.75rem; margin: 0; letter-spacing: 0.02em;">
                CaseMind AI — Multi-Agent Investigation Assistant<br>
                <span style="font-size: 0.65rem; letter-spacing: 0.06em;">
                    POWERED BY GROQ AI
                </span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===========================================================================
#  Main Application Entry Point
# ===========================================================================
def main():
    """Run the CaseMind AI Streamlit application."""

    # Inject custom theme
    inject_custom_css()

    # Inject animated background layer (purely cosmetic, no logic impact)
    render_background_fx()

    # Initialize session state
    init_session_state()

    # Render sidebar (case configuration)
    render_sidebar()

    # Render main page sections
    render_hero()
    render_upload_section()
    render_progress()
    render_dashboard()
    render_activity_panel()
    render_image_analysis_results()
    render_investigation_graph()
    render_investigation_results()
    render_footer()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
