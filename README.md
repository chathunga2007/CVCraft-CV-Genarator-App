# CVCraft — Professional Desktop CV & Resume Builder

> **"Build. Craft. Get Noticed."**

**CVCraft** is an offline-first, commercial-grade desktop application engineered for crafting, customizing, analyzing, and exporting high-impact professional CVs and resumes.

Built with **Python 3.13**, **PyQt6**, **SQLite3**, **ReportLab (Vector Multi-Page PDF Engine)**, and **PyMuPDF (Real-time Live Canvas Rendering)**.

---

## Key Features

### 1. 3-Column Powerhouse Workspace
* **Left Column:** Section navigation (Personal Info, Summary, Experience, Education, Skills, Projects, Certifications, Languages, Achievements, Volunteer, References, Custom Sections) with live completion indicators.
* **Center Column:** Dynamic form editor with instant validation, character counts, and AI-powered enhancements.
* **Right Column:** High-DPI real-time live preview powered by PyMuPDF and ReportLab, featuring page-by-page navigation (Page 1 of N), zoom in/out, and fit-to-width.

### 2. 8 Distinct Professional Architectural Templates
* **Modern Tech:** Clean two-column split with accent sidebar for technical skills.
* **Minimalist Clean:** Sophisticated single-column with refined typography and airy spacing.
* **Executive Leadership:** High-contrast header banner designed for senior leaders and managers.
* **Corporate Professional:** Structured classic 2-column layout with clean divider rules.
* **Creative Designer:** Vibrant accent bars, modern skill pills, and creative portfolio highlights.
* **Software Engineer:** Tech-focused layout with monospace accents, terminal style headers, and repository links.
* **Academic & Research:** Strict single-column academic format emphasizing education, research, and publications.
* **ATS-Friendly Optimized:** 100% linear OCR-friendly structure with zero columns or confusing graphical boxes for maximum automated parsing success.

### 3. "Tailor My CV" ATS Analysis Engine
* Paste any target job description.
* Calculates matching technical skills and keywords.
* Identifies missing critical keywords.
* Checks ATS formatting compatibility (header hierarchy, contact detectability, word count).
* One-click keyword integration directly into your CV skills.

### 4. Offline-First AI Assistant
* **AI Improve Summary:** Elevates tone, adds executive presence, and uses high-impact action verbs.
* **AI Polish Experience Bullets:** Reformats job duties into the **STAR method** (Situation, Task, Action, Result) with measurable metrics.
* **AI Role Skill Suggester:** Generates top industry competencies for any target job role.
* **Strict Confirmation Requirement:** No AI recommendation touches your document without your explicit review and approval.
* Works 100% offline out-of-the-box, with optional support for Google Gemini or Groq Cloud API keys.

### 5. Version Control & Job-Specific Revisions
* Create unlimited job-specific versions (e.g. *Frontend Engineer*, *Backend Lead*, *Consultant*).
* Duplicate existing CVs with a single click.
* Full Undo / Redo support (`Ctrl + Z` / `Ctrl + Y`).

### 6. Privacy & Data Ownership
* 100% local persistence in SQLite (`data/cvcraft.db`).
* Zero telemetry and zero cloud dependencies.
* Export and import lossless `.cvcv` document files.
* Create full portable system backups (`.zip`) and restore with zero data loss.

---

## Installation & Running

### Requirements
* Python 3.10+ (Tested on Python 3.13)
* Windows, macOS, or Linux

### Setup
```bash
# Clone or navigate to the project directory
cd "d:\CV Generator"

# Install dependencies
pip install -r requirements.txt

# Run CVCraft
python run.py
```

### Keyboard Shortcuts
* `Ctrl + N`: Create New CV
* `Ctrl + S`: Save Active CV
* `Ctrl + E`: Export PDF
* `Ctrl + Z`: Undo Edit
* `Ctrl + Y`: Redo Edit

---

## Layered Architecture
```
UI (PyQt6 / Custom Theme Engine)
       ↓
Controllers & Views (WorkspaceView, DashboardView, LivePreviewWidget)
       ↓
Services (CVService, PDFService, ATSService, AIService, ImportExportService)
       ↓
Repositories (CVRepository, SettingsRepository)
       ↓
Database (SQLite3 `data/cvcraft.db`)
```

---
**CVCraft** — *Build. Craft. Get Noticed.*
