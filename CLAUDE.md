# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git Hygiene

**Always run `git fetch --all` before starting any task.** Check whether the current branch or `main` is behind its remote counterpart and inform the user if so. Never base work on a stale local state.

## Project Overview

Internal tool for automating the insurance quote generation process (Angebots-Erstellungs-Prozess) for an insurance broker. The system processes incoming customer emails (.msg/.eml), extracts structured information, matches against product logic, invokes a calculation engine, and generates quotes.

**Business Flow:**
```
Email → Extract (LOB, RiskType, BusinessType, RatingFactors) → Match ProductLogic → Calculate → Generate Offer
```

## Technology Stack

- **Frontend:** React 19 + TypeScript + Vite + Tailwind CSS
- **Backend:** Python 3.12 + FastAPI (not yet scaffolded)
- **Database:** PostgreSQL 16 (Docker Compose)
- **Package Manager:** uv (Python), npm (Frontend)
- **Linting:** Ruff (Python), ESLint (Frontend)
- **DB Access (dev):** Postgres MCP Server (`crystaldba/postgres-mcp`)

## Dev Commands

```bash
# Frontend
cd frontend && npm install   # Install dependencies
cd frontend && npm run dev   # Vite dev server → http://localhost:5173

# Python setup
uv sync                      # Install Python dependencies
source .venv/bin/activate    # Activate virtual environment

# Database
docker compose up -d         # Start PostgreSQL on :5432

# Linting
uv run ruff check .          # Python lint
uv run ruff check --fix .    # Python lint with auto-fix
uv run ruff format .         # Python format
cd frontend && npm run lint  # Frontend lint

# Pre-commit
uv run pre-commit run --all-files   # Run all hooks manually
```

## Architecture

Follows **lightweight Domain-Driven Design** with clear separation of Domain, Infrastructure, and Application Logic. MVP-first, multi-product-capable.

### Core Data Model (7 entities, defined in `db/migrations/001_initial_schema.sql`)

| Entity | Purpose |
|---|---|
| `LineOfBusiness` | Insurance category (e.g., commercial liability) |
| `Product` | Insurance product offering (versioned), belongs to a LoB |
| `RiskType` | Type of risk within a Product |
| `ProductRule` | Declarative rule-based logic for product matching |
| `RatingFactor` | Variables affecting pricing (e.g., square footage) |
| `CustomerRequest` | Structured data extracted from a customer inquiry |
| `Offer` | Generated quote with frozen rating snapshot |

### Service Architecture (5 services, not yet implemented)

| Service | Responsibility |
|---|---|
| **Email Intake Service** | Receives and ingests customer emails |
| **Extraction Service** | Parses emails → structured `CustomerRequest` (via LLM) |
| **Product Logic Service** | Matches `CustomerRequest` against `ProductRule`s |
| **Rating Service** | Invokes calculation engine with matched product + factors |
| **Offer Service** | Generates and stores the final `Offer` |

### Frontend

The frontend (`frontend/`) is a React 19 app with two main components:
- **UploadForm** — Drag-and-drop file upload for .msg/.eml files
- **ResultCard** — Displays extraction results (classification, sender, extracted fields)

The frontend expects a backend API at `http://localhost:8000/upload` (POST, multipart/form-data).

### Design Principles

- Rule-based product logic (configurable in DB via `ProductRule`, not hardcoded)
- Product versioning via `(code, version)` — offers reference a specific version
- Calculation logic decoupled from product definitions
- Full audit trail: `raw_email_body`, `extraction_meta`, `rating_snapshot`

## Key Files

- `task` — Architecture specification (German), primary design document
- `feature/postgress` — Database/MCP setup specification
- `db/migrations/001_initial_schema.sql` — Initial PostgreSQL schema (7 tables)
- `docker-compose.yml` — PostgreSQL 16 service (credentials: `myuser`/`mypassword`/`mydb`)
- `frontend/src/api.ts` — API client interface defining the backend contract
- `examples/` — Sample insurance inquiry emails (.eml, .msg)