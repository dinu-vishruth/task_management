# Task Management System (Professional Edition)

A high-performance **Flask** REST API with **JWT** authentication, **MNC-style** professional admin management, **Broadcast (Global) Tasks**, and a **vanilla HTML/CSS/JS** frontend served directly by the backend.

## Key Features

1.  **Professional Admin CLI**: Secure, command-line based user provisioning and role management (no insecure environment variables).
2.  **Broadcast (Global) Tasks**: Administrators can assign tasks to all users at once by creating "Global Tasks".
3.  **Read-Only Security**: Tasks assigned by administrators are strictly read-only for regular users.
4.  **Structured Admin Dashboard**: Admins see a clear separation between their broadcasted tasks and individual user tasks.
5.  **Simplified Deployment**: The Flask backend serves the frontend static files automatically at the same port.
6.  **Interactive API Docs**: Built-in **Swagger UI** for testing and exploration.

## How the pieces fit together

1.  **`app.py`**: The application factory. It initializes **SQLAlchemy**, **JWT**, and **Swagger**, registers **blueprints**, and configures the backend to serve the **`frontend/`** directory.
2.  **`utils/cli.py`**: Contains the **`flask admin`** command group for secure, professional user management from the terminal.
3.  **`models/`**: Define **User** (with `last_login_at` audit field) and **Task** (with `is_global` flag).
4.  **`routes/`**: Implementation of versioned API endpoints (`/api/v1/...`) with strict **RBAC** (Role-Based Access Control).
5.  **`database/`**: Handles database initialization (`create_all`).

## Tech Stack

| Layer        | Choice                                      |
|-------------|---------------------------------------------|
| Backend     | Python 3, Flask 3                           |
| ORM / DB    | Flask-SQLAlchemy; SQLite (default)          |
| Auth        | JWT (flask-jwt-extended), Werkzeug hashing  |
| API docs    | Swagger UI via Flasgger (`/apidocs`)        |
| Frontend    | Static HTML, CSS, JavaScript (served by Flask) |

## Project Structure

```text
task_management/
├── backend/
│   ├── app.py                 # App factory & frontend serving
│   ├── config.py              # Configuration
│   ├── utils/
│   │   ├── cli.py             # Professional Admin CLI
│   │   └── decorators.py      # RBAC / JWT decorators
│   ├── routes/                # API blueprints
│   ├── models/                # Database models
│   └── database/              # DB init
├── frontend/                  # Static assets (HTML/CSS/JS)
└── README.md
```

## Setup & Running

### 1. Prerequisites
- **Python 3.10+**

### 2. Environment Setup
From the project root:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Professional Admin Provisioning (MNC Style)
We use a secure CLI to manage administrators. Avoid default credentials in `.env` files.

**Create your first admin:**
```powershell
cd backend
$env:FLASK_APP='app.py'; flask admin create
```
*(Follow the interactive prompts to set your username and password securely)*

**Other Admin Commands:**
- `flask admin list`: Show all administrators.
- `flask admin promote <username>`: Make an existing user an admin.
- `flask admin reset-password <username>`: Securely reset any user's password.

### 4. Run the Application
```powershell
cd backend
python app.py
```
**Access the app at**: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Features Overview

### Global Tasks
When an **Admin** creates a task, it is automatically marked as `is_global=True`. These tasks appear in every user's task list instantly. They are **read-only** for regular users to prevent unauthorized changes to corporate assignments.

### Structured Dashboard (Admin View)
Administrators see their own "Global Administrative Tasks" in one section and all other "Individual User Tasks" in another, preventing visual clutter when managing large teams.

## API Documentation (Swagger)
Explore the API endpoints directly at:
**[http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)**

## Security Notes
- **Stateless Auth**: Uses JWT (JSON Web Tokens) for all protected routes.
- **Encrypted Passwords**: PBKDF2 hashing via Werkzeug.
- **Strict RBAC**: Route-level decorators prevent users from modifying admin-assigned tasks.
- **No Insecure Seeding**: Credentials are set via protected CLI commands, not plain-text environment files.

---

## Scalability (Conceptual)
This architecture is designed for growth:
- **Statelessness**: Ready for horizontal scaling with a Load Balancer (NGINX/GCP/AWS).
- **PostgreSQL Ready**: Simply swap the `DATABASE_URL` in `config.py` for high-concurrency production use.
- **Separation of Concerns**: Clean separation between Logic, Models, and API Routes.

---
## License
Educational / Assignment Use.
