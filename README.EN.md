DDD Calculator for Bunkering — FastAPI + Jinja UI

Overview
- Clean-architecture FastAPI app to calculate due dates using DDD (Days after Delivery) terms for bunkering.
- Ships with a lightweight Jinja-based web UI styled in a bright, glassy tone (inspired by pdfm.asdv.cx/pdf-merger).

Run (development)
- Create a venv and install deps:
  - python -m venv .venv
  - .venv\Scripts\activate
  - pip install -r requirements.txt
- Start server:
  - uvicorn app.main:app --reload
- Open UI: http://127.0.0.1:8000/

Using the Web UI
- Date input uses segmented fields (YYYY-MM-DD).
  - After typing 4 digits for the year, focus moves to month; after month, to day.
  - On submit, values are validated and combined into ISO format.
- Payment Term dropdown (DDD/COD/CIA) fills available width across browsers using `-webkit-fill-available` and `-moz-available`.
- Days (for DDD) appears inline on the same row and is enabled only when DDD is selected.
- Sticky form: submitted values remain populated after calculation and validation errors.

Project Layout (clean layering)
- app/
  - core/           - settings, app factory helpers
  - api/            - FastAPI routers/deps (health, etc.)
  - web/            - web pages router (Jinja rendering)
  - templates/      - Jinja templates (`base.html`, `index.html`)
  - static/         - static assets (CSS)
  - domain/         - domain entities/value objects (pure Python)
  - use_cases/      - application services (DDD calculation)
  - infrastructure/ - adapters for external systems (optional)

Endpoints
- GET /v1/health — readiness check
- GET / — web UI (form)
- POST /calculate — form submit (server-side calculation)

Design Notes
- Pretendard font, light blue gradient background, glass card, pill gradient primary button
- Dropdown width: `#term_kind { width: 100%; -webkit-fill-available; -moz-available; }`

Next Steps
- Add business-day/holiday rolling and month-end handling options
- Support a single-field input like "30ddd" alongside segmented mode
- Add unit tests for domain/use-cases/routers
