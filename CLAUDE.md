# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git Hygiene

**Always run `git fetch --all` before starting any task.** Check whether the current branch or `main` is behind its remote counterpart and inform the user if so. Never base work on a stale local state.

## Project Status

This is a new project in early stages of development. As the project evolves, this file should be updated with:
- Common commands (build, lint, test, etc.)
- High-level architecture and design decisions
- Project-specific conventions and patterns
- Key dependencies and their purposes

## Current State

- **Stack**: React + TypeScript (frontend), Python + FastAPI (backend)
- **Build System**: Vite (frontend)
- **Package Manager**: uv (backend), npm (frontend)
- **Testing Framework**: To be determined

## Architecture

```
frontend/   React + TypeScript + Tailwind, Vite dev server
backend/    FastAPI, single POST /upload endpoint
              - Parses .eml (stdlib) and .msg (extract-msg)
              - Calls Claude API (anthropic SDK) for classification + field extraction
              - Returns ExtractionResult JSON to frontend
```

## Dev Commands

```bash
# Frontend
cd frontend && npm run dev         # Vite dev server on http://localhost:5173

# Backend — first-time setup
cd backend && uv venv .venv --python 3.12
uv pip install -r requirements.txt

# Backend — run
cd backend && ANTHROPIC_API_KEY=sk-... .venv/bin/uvicorn main:app --reload
```

## Getting Started

1. Set `ANTHROPIC_API_KEY` in your environment (or prefix the uvicorn command above)
2. Start backend: `cd backend && .venv/bin/uvicorn main:app --reload`
3. Start frontend: `cd frontend && npm run dev`
4. Open http://localhost:5173 and upload an `.eml` or `.msg` insurance inquiry

## Future Updates

Update this file whenever:
- Setting up build/test/lint infrastructure
- Making significant architectural decisions
- Establishing project conventions
- Adding major dependencies or integrations
