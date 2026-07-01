# AGENTS.md

Instructions for future Codex tasks in this repository.

## Project purpose

This is a portfolio-ready sports business analytics project for the fictional Denver Summit FC. Preserve its core story: ticket sales, CRM, attendance, campaigns, retention, and renewals should connect through auditable customer, match, ticket, and campaign keys.

All data must remain synthetic. Never add real customer personal data or credentials.

## Project structure

- `generate_data.py` creates the six CSV datasets in `data/`.
- `database_setup.py` recreates `data/denver_summit_fc.db` from those CSV files.
- `app/dashboard.py` contains the five-view Streamlit dashboard.
- `sql/` contains standalone SQLite analyses.
- `screenshots/` stores portfolio images.
- `README.md` is the public project narrative and runbook.

Treat generated CSV files and the SQLite database as reproducible outputs. When the schema changes, update the generator, database loader, SQL, dashboard, and README together.

## Coding style

- Target Python 3.10+ and use four-space indentation.
- Prefer `pathlib.Path` over string-built file paths.
- Use descriptive snake_case names and short functions with docstrings.
- Add type hints to public helpers where they improve clarity.
- Keep synthetic generation deterministic by using the existing seeded NumPy generator.
- Use vectorized Pandas operations for aggregation and filtering when practical.
- Keep SQL keywords uppercase, use explicit aliases, and organize complex work with CTEs.
- Keep dashboard metric definitions visible in code and consistent with the README.
- Reuse the dashboard color constants and `style_chart()` for new visualizations.
- Comment business rules or non-obvious calculations; do not narrate obvious syntax.
- Do not introduce secrets, external APIs, or network dependencies.

## Data model expectations

- IDs are stable strings with prefixes: `C`, `T`, `M`, `A`, `CMP`, and `CV`.
- Monetary fields are numeric and rounded to two decimals at dataset boundaries.
- Store dates in CSV as ISO `YYYY-MM-DD` values.
- Ticket revenue is `quantity * unit_price`.
- Attendance cannot exceed issued ticket quantity.
- Match ticket quantity should not exceed match capacity.
- Campaign conversions imply a click, and clicks imply an open.
- Renewal likelihood is a 0–100 score.

## Validation commands

Run from the repository root:

```powershell
python -m compileall generate_data.py database_setup.py app
python generate_data.py
python database_setup.py
streamlit run app/dashboard.py
```

For a non-interactive server smoke test:

```powershell
python -m streamlit run app/dashboard.py --server.headless true --server.port 8501
```

After data-model changes, also verify:

- All six CSV files exist and contain rows.
- All six SQL files execute against `data/denver_summit_fc.db`.
- `tickets.quantity` never exceeds available match inventory in aggregate.
- `attendance.tickets_scanned <= attendance.tickets_issued`.
- Campaign funnel counts satisfy `converted <= clicked <= opened <= sent`.
- All dashboard pages load without Python or browser-console errors.

## Change guidelines

- Preserve beginner-friendly local setup; avoid infrastructure that is not needed.
- Prefer extending the existing data model over adding disconnected mock totals.
- If a KPI definition changes, document the new definition in `README.md`.
- If a chart is added, give it a decision-oriented title and useful hover details.
- Keep pages useful at common laptop widths and avoid horizontal scrolling.
- Update screenshots when a visible dashboard change is substantial.

