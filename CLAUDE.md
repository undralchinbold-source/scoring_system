# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

**Prerequisites:** Python 3.14, PostgreSQL 16 (via Docker)

```bash
# Start PostgreSQL
docker run --name postgres16 -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin123 \
  -e POSTGRES_DB=scoring_db -p 5432:5432 -d postgres:16

# Install dependencies
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # then edit with your DB credentials

# Apply migrations and start
flask db upgrade
python run.py  # runs on http://127.0.0.1:5001
```

## Common Commands

```bash
# Run the server
python run.py

# Database migrations
flask db migrate -m "description"   # generate migration
flask db upgrade                     # apply migrations
flask db downgrade                   # rollback one step
```

## Architecture

**Flask application factory** (`app/__init__.py`): `create_app()` initializes extensions (SQLAlchemy, Flask-Migrate, JWT), imports all models for Alembic detection, and registers blueprints. `FLASK_ENV` selects the config class (`development` / `production`).

**Extensions** (`app/extensions.py`): Three singletons — `db` (SQLAlchemy), `migrate` (Flask-Migrate), `jwt` (JWTManager) — initialized separately from the app to avoid circular imports.

**Auth flow**: `POST /api/auth/login` issues a JWT with `identity=user.id` (UUID string) and `additional_claims={role, email}`. All protected endpoints use decorators from `app/utils/decorators.py`.

**Role system** (`app/utils/decorators.py`):
- `any_role_required` — allows `admin` or `super_user`
- `super_user_required` — restricts to `super_user` only
- `current_user_id()` — returns the requesting user's UUID from the JWT identity

**ML scoring pipeline** (`app/routes/predict.py`):
- `POST /api/predict` runs an ML model loaded lazily from `app/ml_model/loan_scoring_model.pkl`
- The `.pkl` bundle contains: `model`, `scaler`, `label_encoder_employment`, `label_encoder_decision`, `model_name`, `model_version`
- Feature engineering computes `amount_to_income_ratio`, `annual_dti`, log transforms before inference
- Gradient Boosting runs on raw features; Logistic Regression requires scaler — controlled by `_requires_scaling`
- Credit score is mapped from approval probability to the range 200–950
- Every prediction writes a `ScoreHistory` record

**Data model relationships:**
- `User` → creates `Client` records, submits `LoanApplication`, creates `ScoreHistory`, generates `AuditLog`
- `Client` → has many `LoanApplication` (restricted delete)
- `LoanApplication` → has many `ScoreHistory` (cascade delete) and `Notification`
- All primary keys are UUIDs; all models live in the `public` PostgreSQL schema

**Route structure:** Each module under `app/routes/` defines a `bp = Blueprint(...)` exported via `app/routes/__init__.py`. URL prefixes: `/api/auth`, `/api/users`, `/api/clients`, `/api/loan-applications`, `/api/score-history`, `/api/notifications`, `/api/audit-logs`, `/api/predict`.

**Loan application statuses:** `pending`, `approved`, `rejected`, `cancelled`

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `FLASK_ENV` | `development` | Selects config class |
| `SECRET_KEY` | `dev-secret-key` | Flask session secret |
| `JWT_SECRET_KEY` | `dev-jwt-secret-key` | JWT signing key |
| `DB_HOST/PORT/NAME/USER/PASSWORD` | localhost/5432/scoring_db/postgres/postgres | PostgreSQL connection |

JWT access tokens expire after **24 hours**.
