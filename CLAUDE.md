# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git Hygiene

**Always run `git fetch --all` before starting any task.** Check whether the current branch or `main` is behind its remote counterpart and inform the user if so. Never base work on a stale local state.

## Project Overview

Internal tool for automating the insurance quote generation process (Angebots-Erstellungs-Prozess) for an insurance broker. The system processes incoming customer emails (.msg/.eml), extracts structured information via Claude AI, matches against product logic, invokes a calculation engine, and generates quotes.

**Business Flow:**
```
Email (.msg/.eml) → Extract (Claude LLM) → Match ProductLogic → Calculate → Generate Offer
```

## Tech Stack

- **Frontend:** React 19 + TypeScript + Vite + Tailwind CSS
- **Backend:** Python 3.12 + FastAPI + Anthropic SDK
- **Database:** PostgreSQL 16 (Docker Compose)
- **Package Managers:** uv (Python), npm (Frontend)
- **Linting:** Ruff (Python), ESLint (Frontend)
- **CI:** GitHub Actions (Ruff check + format on push/PR to main)

## Dev Commands

```bash
# Frontend
cd frontend && npm install         # Install dependencies
cd frontend && npm run dev         # Vite dev server → http://localhost:5173
cd frontend && npm run build       # Production build
cd frontend && npm run lint        # ESLint

# Backend — first-time setup
cd backend && uv venv .venv --python 3.12
uv pip install -r requirements.txt

# Backend — run
cd backend && ANTHROPIC_API_KEY=sk-... .venv/bin/uvicorn main:app --reload  # API → http://localhost:8000

# Database
docker compose up -d               # PostgreSQL on :5432 (myuser/mypassword/mydb)

# Python linting
uv run ruff check .                # Lint
uv run ruff check --fix .          # Lint with auto-fix
uv run ruff format .               # Format
uv run pre-commit run --all-files  # Run all pre-commit hooks
```

## Architecture

```
frontend/   React 19 + TypeScript + Tailwind, Vite dev server
              - UploadForm: drag-and-drop .msg/.eml upload
              - ResultCard: displays extraction results
              - Calls POST http://localhost:8000/upload

backend/    FastAPI, single POST /upload endpoint
              - Parses .eml (stdlib email.parser) and .msg (extract-msg)
              - Calls Claude API (anthropic SDK) for classification + field extraction
              - Returns ExtractionResult JSON to frontend
```

Follows **lightweight Domain-Driven Design** with clear separation of Domain, Infrastructure, and Application Logic. MVP-first, multi-product-capable.

### Data Model Hierarchy (defined in `db/migrations/001_initial_schema.sql`)

```
LineOfBusiness → Product (versioned) → RiskType
                    ├── ProductRule (declarative matching rules)
                    └── RatingFactor (pricing variables)

CustomerRequest → Offer (with frozen rating_snapshot)
```

### Planned Service Architecture (not yet implemented)

| Service | Responsibility |
|---|---|
| **Email Intake Service** | Receives and ingests customer emails |
| **Extraction Service** | Parses emails → structured `CustomerRequest` (via LLM) |
| **Product Logic Service** | Matches `CustomerRequest` against `ProductRule`s |
| **Rating Service** | Invokes calculation engine with matched product + factors |
| **Offer Service** | Generates and stores the final `Offer` |

### Design Principles

- Rule-based product logic (configurable in DB via `ProductRule`, not hardcoded)
- Product versioning via `(code, version)` — offers reference a specific version
- Calculation logic decoupled from product definitions
- Full audit trail: `raw_email_body`, `extraction_meta`, `rating_snapshot`

## Key Files

- `task` — Architecture specification (German), primary design document
- `feature/postgress` — Database/MCP setup specification
- `backend/main.py` — FastAPI endpoint with Claude AI extraction logic
- `frontend/src/api.ts` — API client interface defining the backend contract
- `db/migrations/001_initial_schema.sql` — PostgreSQL schema (7 tables)
- `docker-compose.yml` — PostgreSQL 16 service
- `examples/` — Sample German insurance inquiry emails (.eml, .msg)