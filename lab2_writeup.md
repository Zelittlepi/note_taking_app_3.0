# Lab 2 — AI-assisted NoteTaker Development

Author: Student (using AI assistant as pair-programmer)
Date: 2025-10-19
Repository: note_taking_app_3.0 (branch: feature/add-summary)

---

## Overview

This document summarizes the development process, decisions, challenges, and lessons learned while building an AI-assisted note-taking web application with features such as AI translation, AI auto-completion, timestamp tracking, and Markdown export. The work was performed with guidance and code generation from an AI assistant (used like GitHub Copilot) and integrated into a Flask web application.

The final application structure (relevant files):

- `src/main.py` — Application entry point, Flask app configuration
- `src/routes/note.py` — Note CRUD routes plus AI and export endpoints
- `src/routes/user.py` — User routes
- `src/services/translation.py` — AI integration (requests-based) for translation and auto-complete
- `src/models/note.py` — Note SQLAlchemy model
- `src/static/index.html` — Frontend UI and JavaScript
- `requirements.txt` — Python package requirements
- `lab2_writeup.md` — This document


## Objectives

1. Integrate AI-powered translation (English ↔ Chinese) without using vendor SDKs where possible.
2. Add AI-powered auto-complete (suggestions, corrections, continuation).
3. Track and display note creation and modification timestamps.
4. Add Markdown export support for single-note and bulk exports (.md files).
5. Prepare documentation summarizing the entire process for grading.


## Development Steps (chronological)

1. Project setup and environment checks
   - Verified repository structure and Python environment.
   - Ensured `python-dotenv` would load environment variables from `.env`.

2. Database and models
   - App originally used SQLite locally and was migrated to use a Supabase PostgreSQL instance (configurable via `DATABASE_URL`).
   - Verified SQLAlchemy models for `User` and `Note`, with `created_at` and `updated_at` timestamps.

3. AI integration
   - Created `src/services/translation.py` to call the GitHub Models API (or other inference endpoints) using `requests` instead of SDKs.
   - Implemented `translate_to_chinese()` and higher-level helpers with robust error handling.
   - Added `auto_complete_note()` to provide suggestions, corrections, and continuation types.
   - Added debugging endpoints to check translation service availability.

4. Frontend features
   - Enhanced `src/static/index.html` to display timestamps in the note editor.
   - Added UI for AI auto-complete with dropdown options: Suggestions, Check & Improve, Continue Writing.
   - Implemented JavaScript functions for calling AI endpoints, handling responses, and updating the editor.

5. Markdown export
   - Implemented backend routes in `src/routes/note.py`:
     - `GET /api/notes/<id>/export` — single note export
     - `GET /api/notes/export-all` — combined bulk export with table of contents
   - Implemented helper functions `generate_note_markdown()` and `generate_all_notes_markdown()` to produce well-formed Markdown with YAML frontmatter, timestamps, and export attribution.
   - Added frontend export button and dropdown in `index.html` including `toggleExportMenu()`, `performExport(type)`, and download logic.

6. Testing and debugging
   - Local runs showed some environment/package installation issues that were resolved by installing required packages (e.g., `flask-cors`, `requests`).
   - Verified endpoints using fetch from the frontend and a demo HTML page included in the repo (`export-demo.html`).


## Challenges & How They Were Addressed

1. Dependency and environment issues
   - Problem: `conda` mirror network errors and missing packages (e.g., `flask_cors`).
   - Solution: Used `pip` where appropriate and validated imports with debug endpoints. Created a local `.env` with necessary tokens and DB URL for local testing.

2. Serverless deployment constraints (Vercel)
   - Problem: Serverless function timeouts and incompatible SDKs (previously using OpenAI official SDK) caused 503 errors.
   - Solution: Rewrote AI calls using the `requests` library and lightweight logic; added debug endpoints to diagnose configuration in serverless environments.

3. Interpreting AI outputs reliably
   - Problem: AI responses sometimes included plaintext or wrapped JSON inside text/code blocks.
   - Solution: Implemented robust parsing in `displayAutoCompleteResults()` to detect JSON inside code fences and fallback to plain text when necessary.

4. UI/UX integration
   - Problem: Need to keep AI loading states and avoid blocking the editor.
   - Solution: Implemented button states, debounced auto-save (2s), and non-blocking fetch requests so the editor remains responsive.


## Lessons Learned

- Using lightweight HTTP clients (requests) is often more predictable in constrained environments (serverless) than large SDKs.
- Always add robust parsing for model outputs; don't assume returned formats will always be JSON.
- Keep the UI responsive: provide loading indicators and non-blocking network calls.
- Environment configuration (`.env`) is critical — ensure tokens and DB URLs are set for both local dev and deployment.


## Files Changed / Added

- `src/routes/note.py` — Added export endpoints and helper Markdown generators.
- `src/static/index.html` — Added export button, dropdown, CSS, and JavaScript handlers for export.
- `export-demo.html` — Demo page explaining and showing the export feature locally (for quick visual verification).
- `lab2_writeup.md` — This writeup (added to repository root).


## How to Run Locally (short guide)

1. Install dependencies (recommended in a virtualenv):

```powershell
pip install -r requirements.txt
```

2. Create a `.env` in repository root (example):

```
FLASK_ENV=development
SECRET_KEY=your_secret_key
GITHUB_AI_TOKEN=your_github_token_here
# Optional, leave empty to use local SQLite
# DATABASE_URL=postgresql://user:pass@host:port/dbname
```

3. Start the app:

```powershell
$env:PYTHONPATH=$pwd
python src\main.py
```

4. Open http://127.0.0.1:5001 in your browser. Create notes, try AI features, and test export.


## Screenshots (optional)

Include screenshots to illustrate steps (you can add these manually):

- Screenshot 1: App main screen with notes list
- Screenshot 2: Note editor showing timestamps and AI buttons
- Screenshot 3: Export dropdown and downloaded .md file opened in editor


## Suggested Improvements & Next Steps

- Add unit tests for export functions (`generate_note_markdown`, `generate_all_notes_markdown`).
- Add authentication & per-user export isolation.
- Add server-side validation & sanitization for Markdown output.
- Add optional ZIP export for multiple files instead of a single combined file.
- Add UI to preview the Markdown before downloading.


## Academic Notes

This writeup documents an AI-assisted development workflow. I used the AI assistant extensively to generate code, debug issues, and craft UI logic. I refined the AI's output where necessary and tested locally to ensure functionality.


---

If you'd like, I can also:
- Add screenshots to `lab2_writeup.md` if you provide images or allow me to generate sample ones.
- Create a small unit test file for Markdown generators and run tests.
- Create a PR-ready commit message and push the changes to the repository.


---

End of lab write-up.
