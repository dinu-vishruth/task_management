# Task Management API (Intern Assignment)

Production-style demo: **Flask** REST API with **JWT** authentication, **role-based access** (`user` / `admin`), **task CRUD**, **Swagger UI**, centralized errors, input validation, and a **vanilla HTML/CSS/JS** frontend.

## How the pieces fit together

1. **`app.py`** builds the Flask app, enables CORS, registers **JWT** error handlers and **global HTTP error** handlers (404/405/500), mounts **blueprints** under `/api/v1/...`, and initializes **Swagger**. On startup it creates tables and optionally **seeds an admin** from environment variables.
2. **`config.py`** centralizes secrets and database URL (SQLite file under `backend/instance/` by default, or `DATABASE_URL` for PostgreSQL).
3. **`extensions.py`** holds a single **`SQLAlchemy`** and **`JWTManager`** instance (avoids circular imports).
4. **`models/`** define **User** (`role`: `user` | `admin`) and **Task** (`user_id` = `created_by`).
5. **`routes/`** implement HTTP handlers: **auth** (register/login/me), **tasks** (CRUD with ownership checks), **admin** (users list/delete). **Flasgger** docstrings describe each endpoint for Swagger.
6. **`utils/decorators.py`** provides **`@jwt_required()`** (from Flask-JWT-Extended) and **`@admin_required`** (JWT + role check). **`utils/validation.py`** keeps request validation in one place.
7. **`database/__init__.py`** runs `create_all()` and optional admin seeding.
8. **`frontend/`** is static-only: **`config.js`** stores the JWT and **`fetch`** calls the versioned API.

## Overview

- **Users** register and receive a JWT. They create, list, update, and delete **only their own** tasks.
- **Admins** can list **all** tasks (with author username) and **list/delete users** (cannot delete themselves via the API).
- API is versioned under **`/api/v1/`**. Passwords are hashed with **Werkzeug** (`generate_password_hash` / `check_password_hash`). Tokens are issued with **Flask-JWT-Extended**.

## Tech Stack

| Layer        | Choice                                      |
|-------------|---------------------------------------------|
| Backend     | Python 3, Flask 3                           |
| ORM / DB    | Flask-SQLAlchemy; SQLite default, PostgreSQL optional |
| Auth        | JWT (flask-jwt-extended), Werkzeug hashing  |
| API docs    | Swagger UI via Flasgger (`/apidocs`)        |
| Frontend    | Static HTML, CSS, JavaScript (no framework) |
| CORS        | flask-cors (dev-friendly defaults)          |

## Project Structure

```text
task_mangaement/
├── backend/
│   ├── app.py                 # App factory, Swagger, error handlers
│   ├── config.py              # Settings (env-based)
│   ├── requirements.txt
│   ├── extensions.py          # db, jwt
│   ├── models/
│   │   ├── user_model.py
│   │   └── task_model.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── task_routes.py
│   │   └── admin_routes.py
│   ├── utils/
│   │   ├── decorators.py      # @admin_required, get_current_user_id
│   │   ├── jwt_helper.py      # Token creation
│   │   └── validation.py      # Input rules
│   └── database/
│       └── __init__.py        # init_db, optional admin seed
├── frontend/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── css/style.css
│   └── js/
└── README.md
```

## Setup (Backend)

1. **Python 3.10+** recommended.

2. Create a virtual environment (from the project root):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

4. Optional: copy `.env.example` to `backend/.env` or `.env` at the repo root and set `SECRET_KEY` / `JWT_SECRET_KEY` to long random strings for real deployments.

5. **Optional admin seed (first run only):** if no admin exists yet, you can set:

   ```env
   ADMIN_SEED_USERNAME=admin
   ADMIN_SEED_PASSWORD=your-strong-password
   ```

   On startup, one admin user is created. Remove these variables afterward in production.

6. Run the API from the **`backend`** directory (so imports resolve correctly):

   ```bash
   cd backend
   python app.py
   ```

   Default URL: `http://127.0.0.1:5000`

7. **SQLite** file location: `backend/instance/app.db` (created automatically).

### PostgreSQL (optional)

Set `DATABASE_URL`, for example:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/taskdb
```

Install a driver, e.g. `pip install psycopg2-binary`, then run migrations implicitly via `db.create_all()` on startup (suitable for this assignment; production apps often use Alembic).

## API Documentation (Swagger)

With the server running, open:

- **Swagger UI:** [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)
- **OpenAPI JSON:** [http://127.0.0.1:5000/apispec_1.json](http://127.0.0.1:5000/apispec_1.json) (can be imported into Postman: *Import → Link*).

Protected routes use header: `Authorization: Bearer <access_token>`.

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Liveness check |
| `POST` | `/api/v1/auth/register` | No | Register (`user` role); returns JWT |
| `POST` | `/api/v1/auth/login` | No | Login; returns JWT |
| `GET` | `/api/v1/auth/me` | JWT | Current user profile |
| `POST` | `/api/v1/tasks` | JWT | Create task |
| `GET` | `/api/v1/tasks` | JWT | List own tasks; **admin** sees all |
| `PUT` | `/api/v1/tasks/<id>` | JWT | Update if owner or admin |
| `DELETE` | `/api/v1/tasks/<id>` | JWT | Delete if owner or admin |
| `GET` | `/api/v1/users` | JWT **admin** | List users |
| `DELETE` | `/api/v1/users/<id>` | JWT **admin** | Delete user (not self) |

### Example: Register

**Request**

```http
POST /api/v1/auth/register HTTP/1.1
Content-Type: application/json

{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secretpass12"
}
```

**Response `201`**

```json
{
  "message": "Registration successful.",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "role": "user",
    "created_at": "2026-03-28T12:00:00"
  },
  "access_token": "<jwt>"
}
```

### Example: Create task

**Request**

```http
POST /api/v1/tasks HTTP/1.1
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "title": "Write README",
  "description": "Include examples"
}
```

**Response `201`**

```json
{
  "message": "Task created.",
  "task": {
    "id": 1,
    "title": "Write README",
    "description": "Include examples",
    "created_by": 1,
    "created_at": "2026-03-28T12:05:00"
  }
}
```

### HTTP status codes used

`200`, `201`, `400`, `401`, `403`, `404`, `409`, `405`, `500` — see JSON bodies for `error` and `message`.

## Frontend

The UI expects the API at **`http://127.0.0.1:5000`** (see `frontend/js/config.js`). Change `API_BASE` if your backend uses another host/port.

Serve the static files with any static server (avoid opening HTML as `file://` URLs for consistent behavior):

```bash
cd frontend
python -m http.server 8080 --bind 127.0.0.1
```

Then open **[http://127.0.0.1:8080](http://127.0.0.1:8080)** (or `http://localhost:8080`). Do **not** use `http://[::]:8080/` — that IPv6 form often triggers `ERR_ADDRESS_INVALID` in the browser.

- **Register / Login** — stores JWT in `localStorage` under `tm_jwt`.
- **Dashboard** — loads `/auth/me` and `/tasks`, supports create / edit / delete via `fetch()`.

## Making a user an admin (manual)

If you did not use `ADMIN_SEED_*`, promote a user in the SQLite file.

**If you have the `sqlite3` CLI** (macOS/Linux; optional on Windows):

```bash
sqlite3 backend/instance/app.db "UPDATE users SET role='admin' WHERE username='alice';"
```

**Without the CLI (works on Windows with only Python):** from the `backend` directory, replace `alice` with your username.

PowerShell:

```powershell
python -c "import sqlite3; c=sqlite3.connect('instance/app.db'); c.execute(\"UPDATE users SET role='admin' WHERE username='alice'\"); c.commit(); print('ok')"
```

bash / cmd:

```bash
python -c "import sqlite3; c=sqlite3.connect('instance/app.db'); c.execute(\"UPDATE users SET role='admin' WHERE username='alice'\"); c.commit(); print('ok')"
```

Or use [DB Browser for SQLite](https://sqlitebrowser.org/) and run the same `UPDATE` against `backend/instance/app.db`.

Then **log out and log in again** so your JWT includes `admin`.

For PostgreSQL, use any SQL client and run the same `UPDATE` against your `users` table.

## Security Notes (assignment scope)

- Passwords are never stored in plain text.
- JWTs must be sent on protected routes; invalid/expired tokens return `401`.
- Role checks enforce admin-only user management and cross-user task access for admins only.
- For production: use strong secrets, HTTPS, rate limiting, structured logging, and regular dependency updates.

---

## Scalability & Operations (conceptual)

This section describes how a system like this could grow beyond a single process and SQLite.

### Microservices

Split responsibilities into services with clear contracts (REST or gRPC), for example: **Auth service** (tokens, users), **Task service** (tasks), **Notification service**. Each service owns its data store; communication is asynchronous (message queues) where appropriate. An **API gateway** routes clients to services and handles cross-cutting auth.

### Redis for caching

Use **Redis** to cache hot reads (e.g. user profile, task list summaries) with TTLs and explicit invalidation on writes. Redis can also back **rate limiting**, **session allowlists** (token blocklist on logout), and pub/sub for real-time updates.

### Docker

Package the API and frontend (e.g. nginx for static files) as **images**, define services in **Docker Compose** (app, db, redis), and use **multi-stage builds** for smaller Python images. Environment-specific config via env vars and secrets, not baked into images.

### Load balancing (e.g. NGINX)

Run multiple **Gunicorn/uWSGI** workers behind **NGINX** (or another LB). NGINX terminates TLS, balances HTTP across instances, and serves static assets. Use **health checks** (`/health`) so unhealthy instances are removed from rotation.

### Cloud (AWS / GCP)

- **Compute:** ECS/EKS, Cloud Run, App Engine, or EC2 with auto-scaling groups.
- **Managed DB:** RDS (Postgres), Cloud SQL — avoid SQLite at scale.
- **Cache:** ElastiCache / Memorystore.
- **Secrets:** AWS Secrets Manager / GCP Secret Manager.
- **Observability:** centralized logs (CloudWatch, Cloud Logging), metrics, tracing (OpenTelemetry).

Horizontal scaling works when **application state** lives outside the process (DB, Redis), and JWT validation remains stateless or uses a shared blocklist for revocation.

---

## License

Educational / assignment use. Adapt as needed for your organization’s policies.
