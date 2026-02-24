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

- **Stack**: React + TypeScript (frontend), Python + FastAPI (backend — not yet scaffolded)
- **Build System**: Vite (frontend)
- **Testing Framework**: To be determined

## Dev Commands

```bash
# Frontend
cd frontend && npm run dev   # Vite dev server on http://localhost:5173

# Backend (not yet scaffolded)
cd backend && uvicorn main:app --reload   # API server on http://localhost:8000
```

## Getting Started

When the project structure is established, document:
1. How to set up the development environment
2. Commands to build and run the application
3. How to run tests and linting
4. How to run individual tests during development
5. Any architecture diagrams or high-level system design

## Future Updates

Update this file whenever:
- Setting up build/test/lint infrastructure
- Making significant architectural decisions
- Establishing project conventions
- Adding major dependencies or integrations
