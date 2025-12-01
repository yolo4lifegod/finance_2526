<!-- Copilot / AI agent instructions for the ASME Finance app -->
# Repo snapshot
- Small Flask app using an application factory in `app.py` and SQLAlchemy models in `models.py`.
- Routes and UI lives in `routes.py` + `templates/` (Jinja2). Forms are in `forms.py` (Flask-WTF).
- DB migrations live in `migrations/` (Alembic / Flask-Migrate). A default SQLite DB is configured in `config.py`.

# High-level architecture (what to know first)
- App factory: `create_app()` in `app.py` — register the blueprint `bp` from `routes.py`.
- Single blueprint `main` (in `routes.py`) contains the web UI and most business logic (reimbursements, purchases, grants, expenditures).
- Models: `models.py` defines domain objects (ReimbursementRequest, PurchaseRequest/Item, Expenditure, Income, Grant*).
- File uploads: handled by `routes.save_file()` and saved under `UPLOAD_FOLDER` from `config.py` — allowed types are `pdf/png/jpg/jpeg`.
- Design teams: static list imported from `design_teams.py` (`DESIGN_TEAMS`) — forms set choices from this list or from DB where applicable.

# Key developer workflows and commands
- Run locally (development): run `python run.py`. `run.py` creates app context and runs `app.run(debug=True)` and calls `db.create_all()` on startup.
- Database (migrations): Alembic scaffold is present in `migrations/`.
  - Typical commands (PowerShell):
    - `$env:FLASK_APP = 'run.py'; flask db migrate -m "message"`
    - `flask db upgrade`
  - Note: `run.py` pushes an app context on import, so `FLASK_APP=run.py` works for the Flask CLI.
- Testing quick smoke: `python test_reimbursement.py` is a simple HTTP-based smoke script that expects a running app at `http://127.0.0.1:5000`.

# Project-specific patterns & conventions
- Route-centric logic: Many business rules are implemented directly inside route handlers (e.g., creating `Expenditure` rows after Reimbursement/Purchase submission); prefer small, well-tested refactors if extracting logic.
- File uploads: `save_file()` prefixes uploaded filenames with a UTC timestamp integer to avoid collisions — when referencing uploaded files check `UPLOAD_FOLDER` for stored filenames.
- Dynamic form items: `PurchaseRequestForm` accepts a `FieldList`, but client-side adds items dynamically (see `static/js/purchase_items.js`). Server-side `routes.purchase_request` also parses `request.form` keys named like `items-0-link`.
- Template naming: templates match routes: `reimbursement_form.html`, `purchase_request.html`, `expenditures.html`, etc. Use those names when adding views.

# Integration points & external dependencies
- Dependencies are in `requirements.txt` (Flask, Flask-WTF, Flask-Migrate, SQLAlchemy). Use the file to install a dev environment.
- Environment variables recognized in `config.py`:
  - `DATABASE_URL` — defaults to `sqlite:///finance.db`
  - `SECRET_KEY` — defaults to `dev-secret-key`
  - `UPLOAD_FOLDER` — defaults to `./uploads`
- Migrations: Alembic config in `migrations/alembic.ini` — apply `flask db upgrade` to bring schema current.

# Guidance for code changes (concise, project-specific)
- If adding a new model: update `models.py`, create a migration (`flask db migrate`) and run `flask db upgrade`.
- If adding a route that accepts file uploads: reuse `save_file()` and validate using `ALLOWED_EXTENSIONS` from `config.py`.
- When modifying forms, mirror field names used in templates and `routes.py` — some handlers read `request.form` directly (non-FieldList fallback). Check `static/js` for client-side field naming.
- Keep business-critical side-effects explicit in routes: e.g., `reimbursement()` creates both `ReimbursementRequest` and an `Expenditure` row. When refactoring, preserve commit ordering and id usage (request commit to get `r.id`).

# Examples (copyable snippets)
- Create app for CLI/migrations (PowerShell):
```
$env:FLASK_APP = 'run.py'
flask db migrate -m "add foo"
flask db upgrade
```
- Save an uploaded file (routes helper): see `routes.save_file(file_storage)` — call before creating DB rows that reference the filename.

# What an AI agent should NOT assume
- Do not assume background jobs or async processing — all operations are synchronous and run in request context.
- Do not assume the presence of users beyond simple form submissions — authentication is not implemented.

# Where to look for detail
- `routes.py`: business logic and user flows (reimbursements, purchases, expenditures, grants)
- `models.py`: DB schema and helpful properties like `Expenditure.total_cost`
- `forms.py`: expected form fields and validators
- `config.py`: runtime configuration and environment variables
- `static/js/purchase_items.js`: client-side dynamic field naming for purchase items

# If unclear, ask the maintainer
- Which environment is canonical for development (virtualenv vs. conda)?
- Are any production deployment steps or secrets management practices expected?

-- End of file
