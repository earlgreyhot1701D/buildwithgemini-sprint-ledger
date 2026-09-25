<div align="center">

<img src="assets/sprint-ledger-banner.png" alt="Sprint Ledger — Hackathon Tracking Agent" width="100%" />

# ⏱️ Sprint Ledger

### A hackathon tracker agent built with Google Agent Development Kit (ADK), Gemini 2.5 Flash, Firestore, and A2UI.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Agent%20Platform-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com)
[![ADK](https://img.shields.io/badge/Built%20with-ADK%20%2B%20agents--cli-34A853)](https://google.github.io/adk-docs/)
[![Firestore](https://img.shields.io/badge/Database-Firestore-FFCA28?logo=firebase&logoColor=black)](https://cloud.google.com/firestore)
[![UI](https://img.shields.io/badge/UI-A2UI%20v0.8%20%2B%20FastAPI-1FB5B7)](https://a2ui.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

</div>

---

**Sprint Ledger** helps developers capture, verify, and track hackathon deadlines and submission requirements with deterministic date calculations, Firestore persistence, checklist tracking, and rich A2UI cards.

## 🎬 Live Agent Demo

[▶️ **Watch the Demo Video**](https://raw.githubusercontent.com/earlgreyhot1701D/buildwithgemini-sprint-ledger/main/sprint-ledger/assets/sprint_ledger_demo.mp4) (or view in repo: [`assets/sprint_ledger_demo.mp4`](assets/sprint_ledger_demo.mp4))

https://raw.githubusercontent.com/earlgreyhot1701D/buildwithgemini-sprint-ledger/main/sprint-ledger/assets/sprint_ledger_demo.mp4

*Watch Sprint Ledger render live side-by-side dashboard cards, toggle interactive Firestore checklist items, evaluate sprint priority deadlines, and query real-time database records.*

### 🎥 How This Demo Was Created (Tooling & Pipeline)

This demo was recorded and produced completely headlessly inside the Linux cloud development environment:

1. **Headless Browser Orchestration ([Playwright](https://playwright.dev/python/))**:
   - An asynchronous Python script (`record_demo.py`) launched a headless Chromium browser instance with `--window-size=1280,800` and automated context video recording (`record_video_dir`).
   - The script navigated to the deployed Cloud Run service URL and waited for network idle to ensure the Firestore `/api/hackathons` payload rendered the side-by-side card grid.
   - It automated human-paced interactions: hovering, toggling a live submission checkbox to show instant strike-through and progress bar recalculation, typing prompts with randomized keystroke latency (`delay=30ms`), and smoothly scrolling to newly generated A2UI cards.
2. **Deterministic Live Prompts Tested**:
   - **Prompt 1 (Core Capability)**: *"What is our highest priority hackathon and what are the remaining submission requirements?"* — Demonstrates deterministic deadline sorting and outstanding requirement extraction.
   - **Prompt 2 (Database Tool Call)**: *"Look up our Global Open Agents Challenge from Firestore and verify what requirements we need to complete."* — Demonstrates dynamic tool execution and real-time Firestore document retrieval over the Agent-to-Agent (A2A) protocol.
3. **Video Encoding & Transcoding ([FFmpeg](https://ffmpeg.org/))**:
   - Playwright outputs raw VP8 `.webm` streams during headless recording.
   - An automated FFmpeg pipeline transcoded the raw capture to universally compatible H.264 / AAC MP4 with high fidelity:
     ```bash
     ffmpeg -y -i raw_capture.webm -c:v libx264 -crf 22 -preset medium -pix_fmt yuv420p assets/sprint_ledger_demo.mp4
     ```
   - Result: A smooth, crisp 48-second 1280x800 MP4 demo weighing only 1.5MB.

## 🌟 Key Features

- **🌐 Single-Page Rules Ingestion**: `fetch_page(url)` securely grabs rules from hackathon platforms (Devpost, dev.to, AWS Builder, etc.) with strict HTML sanitization and timeout protections.
- **🛡️ Evidence-First Extraction**: Extracts deadline quotes, timezones, and checklist criteria verbatim. Missing items are strictly marked `"NOT FOUND"`—never hallucinated.
- **📐 Deterministic Date Math**: Never lets the LLM perform date math. Python's standard `datetime` and `zoneinfo` parse deadlines, compute UTC timestamps, calculate days remaining, and set a **Ship-By Date** (`deadline - 1 day`).
- **🗄️ Firestore Persistence**: Saves and organizes tracked hackathons and tracks checklist progress.
- **🧠 Cross-Session Memory**: Integrates Vertex AI Memory Bank (`PreloadMemoryTool` & callbacks) to remember developer preferences, handles, and tech stacks across conversations.
- **🎨 A2UI Rich Cards & Custom Frontend**: Renders hackathon countdowns, checklists, and status badges in a branded, responsive web interface.

---

## 🏗️ Architecture & Flow

```mermaid
flowchart TD
    User(["Developer (Prompt / Rules URL)"]) --> Agent["Sprint Ledger Agent (ADK / Gemini 2.5)"]
    Agent <--> Memory["Vertex AI Memory Bank (User Preferences & Handles)"]
    
    subgraph Ingestion & Verification
        Agent -->|"fetch_page(url)"| Web["Hackathon Rules Page"]
        Web -->|"HTML content"| Sanitize["Sanitizer & Verbatim Extractor"]
        Sanitize -->|"deadline, timezone, criteria"| DateMath["Deterministic Date Engine (Python datetime)"]
        DateMath -->|"UTC, days left, ship-by date"| Confirm{"User Explicit Confirmation"}
    end
    
    Confirm -->|Approved| DB[("Google Cloud Firestore")]
    DB --> CardGen["A2UI v0.8 Schema Generator"]
    CardGen --> UI["Custom FastAPI Chat Web UI (Port 8080)"]
```

### Project Structure

```text
sprint-ledger/
├── app/
│   ├── agent.py               # Main ADK agent logic, tools, and callbacks
│   ├── db.py                  # Firestore database client & CRUD operations
│   ├── fast_api_app.py        # FastAPI backend server
│   └── app_utils/             # App utilities and helpers
├── frontend/                  # Custom chat web interface (A2UI & brand styling)
│   ├── static/index.html      # Tailored frontend with live A2UI renderer
│   ├── main.py                # FastAPI proxy server
│   └── requirements.txt
├── tests/                     # Unit and integration tests
├── seed_firestore.py          # Firestore database initialization script
├── agents-cli-manifest.yaml   # Agent metadata and deployment specification
├── pyproject.toml             # Project dependencies (managed with uv)
├── Dockerfile                 # Container image specification
└── README.md
```

---

## 🛠️ Built With

- **Framework**: [Google ADK (Agent Development Kit)](https://google.github.io/adk-docs/) & `agents-cli`
- **Model**: Gemini 2.5 Flash on Vertex AI
- **Database**: Google Cloud Firestore (Native mode)
- **Memory**: Vertex AI Memory Bank
- **UI**: A2UI (Agent-to-User Interface) + Custom FastAPI / Cloud Run frontend

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [agents-cli](https://google.github.io/agents-cli/guide/getting-started/): `uv tool install google-agents-cli`
- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install) authenticated to your project:
  ```bash
  gcloud auth application-default login
  ```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Local Development

Run the agent locally with the ADK playground:
```bash
uv run agents-cli playground
```

Or run the custom web frontend:
```bash
cd frontend
uv run uvicorn main:app --reload --port 8080
```

---

## 🧪 Testing

Run unit and integration tests:
```bash
uv run pytest tests/unit tests/integration
```

---

## 🚢 Deployment

Deploy to Vertex AI Agent Runtime:
```bash
gcloud config set project <your-project-id>
agents-cli deploy
```
