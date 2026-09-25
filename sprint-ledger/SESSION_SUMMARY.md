# 📋 Sprint Ledger: Build Session Summary & Next Steps

**Date**: September 25, 2026  
**Participant**: [@earlgreyhot1701D](https://github.com/earlgreyhot1701D)  
**Repository**: [earlgreyhot1701D/buildwithgemini-sprint-ledger](https://github.com/earlgreyhot1701D/buildwithgemini-sprint-ledger)  
**Event**: Google Cloud Build with Gemini World Tour (Track 3: Agent-First Apps)

---

## 🎯 What Was Built

**Sprint Ledger** is an agentic hackathon tracking assistant built with the Google Agent Development Kit (ADK) and `agents-cli`. It solves the common problem of missed deadlines, misunderstood rules, and ambiguous submission criteria by providing a deterministic, evidence-based capture and tracking workflow.

### Core Architecture & Capabilities

1. **Deterministic Date Math & Guardrails**:
   - The LLM is never allowed to do arithmetic on dates.
   - Python standard libraries (`datetime`, `zoneinfo`) parse deadline strings into UTC, calculate the exact days remaining, and automatically generate a **Ship-By Date** (`deadline - 1 day`).
   - Timezones and ambiguity are explicitly handled with warnings.

2. **Evidence-First Rules Ingestion (`fetch_page`)**:
   - Secure single-page HTTP GET with timeout, script/style stripping, and length checks.
   - Fallback warning prompting manual paste when a page is a client-side JavaScript Single Page App (SPA).
   - Strict extraction schema: missing information is strictly marked `"NOT FOUND"`—never hallucinated.
   - Explicit user confirmation gate before saving into the database.

3. **Persistence with Cloud Firestore**:
   - Provisioned Google Cloud Firestore in native mode (`us-east1`).
   - Hardcoded GCP project ID in `app/db.py` to prevent Agent Platform project number collision.
   - Seeded initial hackathons (`seed_firestore.py`).
   - Tools to list, inspect, and toggle submission checklist items (`toggle_checklist_item`).

4. **Cross-Session Long-Term Memory (Vertex AI Memory Bank)**:
   - Configured `PreloadMemoryTool` and turn callback `generate_memories_callback`.
   - Reused persistent Memory Bank instance to remember developer handles, preferences, and preferred tech stacks (`Google Cloud & AWS`) across sessions.

5. **Tailored A2UI Web Frontend**:
   - Integrated A2UI v0.8 cards on the agent (`A2uiSchemaManager`).
   - Branded chat interface built with FastAPI proxy and styled to custom specs:
     - Color Palette: Deep navy (`#0A1F2E`), midnight slate (`#061720`), turquoise (`#1FB5B7`), warm paper cards (`#F1E8D2`), sienna accents (`#E85A1F`).
     - Typography: Google Fonts (`Cinzel`, `Source Serif 4`, `JetBrains Mono`).
     - Ethos principles bar: *Evidence precedes conclusions*, *Structural determinism precedes intelligence*, *Human authority remains visible*.
   - Renders live countdown badges, checklist toggles, and metadata cards.

6. **Devpost Discovery & Media Storage**:
   - `fetch_devpost_hackathons()` tool to discover active public hackathons.
   - Public Google Cloud Storage bucket (`gs://sprint-ledger-media-1625fe9e`) configured with CORS for generated cover images.

---

## 📦 What Was Published

1. **GitHub Repository**:
   - Initialized a clean, public repository: [buildwithgemini-sprint-ledger](https://github.com/earlgreyhot1701D/buildwithgemini-sprint-ledger)
   - Authenticated via GitHub CLI device flow under `@earlgreyhot1701D`.
   - Comprehensive `.gitignore` protecting secrets, virtualenvs, and credentials.
   - Included full `project_brief.md` specification in root and project directories.
   - Added custom branded 16:9 banner matching frontend UI aesthetics.
   - Added interactive Mermaid architecture flowchart and technology shield badges.
   - Tagged repo with discoverability topics: `gemini-api`, `google-adk`, `agent-platform`, `firestore`, `a2ui`, `hackathons`, `agents-cli`.

2. **Swag & Gallery Submission**:
   - Pre-filled Google Form generated and submitted with repository link, project title, and participant details.

---

## 🔮 Suggested Next Steps & Enhancements

### 1. Cover Art Generation (Imagen on Vertex AI)
- **Current State**: `generate_cover_image(hackathon_id)` is stubbed in `app/agent.py`.
- **Next Step**: Connect it to Vertex AI Imagen (`imagegeneration@006` or `gemini-3.1-flash-lite-image`).
- Have it generate a custom 16:9 dev.to/blog-style cover graphic based on the hackathon theme, upload it to `gs://sprint-ledger-media-1625fe9e`, and attach the public URL to the Firestore document.

### 2. GitHub Repo & License Validation Tool
- **Current State**: Mentioned in `project_brief.md` as a planned feature.
- **Next Step**: Implement a tool using GitHub's public REST API (`GET /repos/{owner}/{repo}`) that verifies:
  - Repository exists and is public.
  - License file is present and matches hackathon open-source rules (e.g., Apache 2.0 or MIT).
  - Automatically check off the *"Public GitHub repository with open-source license"* item in the hackathon's checklist.

### 3. Automated Notifications & Calendar Sync
- **Next Step**: Add an export or webhook notification tool:
  - Generate an `.ics` calendar file with alarms for the **Ship-By Date** (`T - 24 hours`) and final deadline.
  - Optional Slack / Discord webhook notification when days remaining drops below 3.

### 4. Deploy Frontend to Cloud Run
- **Current State**: Frontend runs locally via FastAPI on port 8080 talking to the local or deployed agent.
- **Next Step**: Containerize the `frontend/` directory with Cloud Build and deploy to Google Cloud Run with an unauthenticated public HTTPS endpoint so anyone can test Sprint Ledger live.

### 5. Multi-User Authentication
- **Next Step**: Add Firebase Auth to the frontend so different users can sign in with GitHub or Google and maintain their own personal Firestore hackathon ledgers.
