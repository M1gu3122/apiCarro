# Repository Guidelines

## Project Structure

- `main.py` creates the FastAPI application and registers routers with their access dependencies.
- `app/api/` defines HTTP routes, `app/models/` contains Pydantic models, and `app/repositories/` handles PostgreSQL queries through psycopg2. For a typical resource, follow `rutas_vehiculos.py`, `vehiculos.py`, and `vehiculos_repo.py`.
- `app/core/database.py` manages database connections. `app/core/security.py` handles JWTs, password hashing, and module-based access checks.

## Local Development

Run these commands from the repository root in PowerShell.

1. `python -m venv myvenv` creates the local virtual environment.
2. `.myvenvScriptspython.exe -m pip install -r requirements.txt` installs dependencies.
3. `.myvenvScriptspython.exe -m uvicorn main:app --reload` starts the development server. Open `http://127.0.0.1:8000/docs` to try endpoints.

Use a development PostgreSQL database with the expected schema. Set `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `SECRET_KEY` in your local `.env`. Keep credentials and tokens out of commits and PRs.

## Coding Style

Use four spaces for indentation, `snake_case` for modules and functions, and `PascalCase` for classes. Follow the surrounding Spanish domain vocabulary in identifiers. Store role names in lowercase (for example, `administrador`, `operador`, `supervisor`); normalize them on creation and update. Keep SQL in repositories and parameterize user-supplied values. When adding a protected router, register it in `main.py` with the appropriate module access dependency.

## Testing

The repository has no checked-in test suite, coverage target, or formatter configuration. Verify changed routes through Swagger UI against the development database. For protected routes, exercise a permitted request, a request without a token, and a request from a user without the required module.

## Commits and Pull Requests

Git history uses short, plain-language subjects in Spanish and English, such as `Fix requirements encoding`. Name the change in the subject. In the PR, summarize the affected routes or models, flag database or configuration changes, list verification steps, and link the related issue when available.
