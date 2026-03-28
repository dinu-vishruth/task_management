"""
Task Management API — Flask application factory.
Run from the `backend` directory:  python app.py
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger

from config import config_by_name
from extensions import db, jwt
from database import init_db
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.task_routes import task_bp
from utils.cli import admin_cli

_root = Path(__file__).resolve().parent
load_dotenv(_root / ".env")
load_dotenv(_root.parent / ".env")


def create_app(config_name=None):
    """Application factory."""
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    if config_name not in config_by_name:
        config_name = "default"

    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder=os.path.abspath(_root.parent / "frontend"),
        static_url_path="",
    )

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    app.config.from_object(config_by_name[config_name])

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}},
    )

    _register_jwt_handlers(app)
    _register_error_handlers(app)

    # Flask merges only one url_prefix per registration — use full API paths here.
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(task_bp, url_prefix="/api/v1/tasks")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/users")

    Swagger(
        app,
        template={
            "swagger": "2.0",
            "info": {
                "title": "Task Management API",
                "description": "JWT auth, RBAC, and task CRUD. Prefix: /api/v1",
                "version": "1.0.0",
            },
            "securityDefinitions": {
                "Bearer": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "description": "Format: Bearer <access_token>",
                }
            },
        },
    )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    init_db(app)
    app.cli.add_command(admin_cli)

    return app


def _register_jwt_handlers(app):
    """Consistent JSON errors for JWT failures."""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": "Token has expired. Please log in again.",
                }
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": "Invalid token.",
                }
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": "Authorization header missing or invalid.",
                }
            ),
            401,
        )


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found.",
                }
            ),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(e):
        return (
            jsonify(
                {
                    "error": "Method Not Allowed",
                    "message": "HTTP method is not allowed for this URL.",
                }
            ),
            405,
        )

    @app.errorhandler(500)
    def server_error(e):
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
        )


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
