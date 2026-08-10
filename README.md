# 🧠 CaseMind AI

**AI Investigation Assistant**

> Upload investigation evidence and let AI analyze documents, chats, and images to generate an investigation report.

---

## 📋 Overview

CaseMind AI is a professional AI-powered investigation assistant built with Streamlit. It helps investigators analyze evidence from multiple sources — documents, images, and chat logs — to construct timelines, identify contradictions, and generate comprehensive investigation reports.

**Current Status:** Multi-Agent Build — Document Agent, Image Agent (Groq Vision), Evidence Agent,
Timeline Agent, and Report Agent are all connected and running live. The UI has been redesigned
with a live agent activity panel, per-image forensic analysis cards, an investigation
entity-relationship graph, an animated risk-scored dashboard, and one-click PDF report export.

---

## 🏗️ Project Structure

```
CaseMind-AI/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── README.md               # Project documentation
│
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
│
├── agents/                 # AI investigation agents
│   ├── __init__.py         # Package initialization
│   ├── document_agent.py   # Document analysis agent
│   ├── image_agent.py      # Image analysis agent
│   ├── chat_agent.py       # Conversational investigation agent
│   ├── timeline_agent.py   # Timeline construction agent
│   ├── evidence_agent.py   # Evidence cross-reference agent
│   └── report_agent.py     # Report generation agent
│
├── utils/                  # Shared utility functions
│   └── __init__.py
│
├── uploads/                # Uploaded evidence files
├── reports/                # Generated investigation reports
└── assets/                 # Static assets (images, icons)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/casemind-ai.git
   cd casemind-ai
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys (when AI features are enabled)
   ```

5. **Run the application:**

   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`.

---

## 🎨 Features

### Current (Foundation)
- ✅ Dark futuristic dashboard theme
- ✅ Sidebar with case creation form
- ✅ Multi-file evidence upload (PDF, TXT, PNG, JPG, JPEG)
- ✅ Professional file display cards
- ✅ Investigation dashboard with metric cards
- ✅ Placeholder investigation results sections
- ✅ Modular agent architecture (stubs)

### Planned (AI Integration)
- 🔲 Google Gemini API integration
- 🔲 Document analysis and entity extraction
- 🔲 Image analysis with Gemini Vision
- 🔲 Automatic timeline construction
- 🔲 Evidence cross-referencing
- 🔲 Contradiction detection
- 🔲 Comprehensive report generation
- 🔲 Conversational investigation chat

---

## 🛠️ Tech Stack

| Component     | Technology         |
|---------------|--------------------|
| Frontend      | Streamlit          |
| Language      | Python 3.9+        |
| AI Engine     | Google Gemini (TBD) |
| Styling       | Custom CSS         |
| PDF Processing| PyPDF2             |
| Image Processing | Pillow          |

---

## 📄 Supported File Types

| Format | Type     | Extension |
|--------|----------|-----------|
| PDF    | Document | `.pdf`    |
| TXT    | Document | `.txt`    |
| PNG    | Image    | `.png`    |
| JPG    | Image    | `.jpg`    |
| JPEG   | Image    | `.jpeg`   |

---

## 👥 Team

Built for **College Competition 2026**

---

## 📜 License

This project is developed for educational and competition purposes.
