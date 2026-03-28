"""Authentication: register, login, current user profile."""
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask_jwt_extended import jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models.user_model import User
from utils.decorators import get_current_user_id
from utils.jwt_helper import create_user_access_token
from utils.validation import validate_email, validate_password, validate_username

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
@swag_from(
    {
        "tags": ["Authentication"],
        "summary": "Register a new user (role: user)",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "required": ["username", "email", "password"],
                    "properties": {
                        "username": {"type": "string"},
                        "email": {"type": "string"},
                        "password": {"type": "string"},
                    },
                },
            }
        ],
        "responses": {
            201: {"description": "User created"},
            400: {"description": "Validation error"},
        },
    }
)
def register():
    data = request.get_json(silent=True) or {}
    ok, username = validate_username(data.get("username"))
    if not ok:
        return jsonify({"error": "Bad Request", "message": username}), 400
    ok, email = validate_email(data.get("email"))
    if not ok:
        return jsonify({"error": "Bad Request", "message": email}), 400
    ok, password = validate_password(data.get("password"))
    if not ok:
        return jsonify({"error": "Bad Request", "message": password}), 400

    if User.query.filter(
        (User.username == username) | (User.email == email)
    ).first():
        return (
            jsonify(
                {
                    "error": "Conflict",
                    "message": "Username or email already registered.",
                }
            ),
            409,
        )

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role="user",
    )
    db.session.add(user)
    db.session.commit()

    token = create_user_access_token(user)
    return (
        jsonify(
            {
                "message": "Registration successful.",
                "user": user.to_public_dict(),
                "access_token": token,
            }
        ),
        201,
    )


@auth_bp.post("/login")
@swag_from(
    {
        "tags": ["Authentication"],
        "summary": "Login and receive JWT",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "required": ["username", "password"],
                    "properties": {
                        "username": {"type": "string"},
                        "password": {"type": "string"},
                    },
                },
            }
        ],
        "responses": {
            200: {"description": "OK"},
            401: {"description": "Invalid credentials"},
        },
    }
)
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password")
    if not username or not password:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Username and password are required.",
                }
            ),
            400,
        )

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return (
            jsonify(
                {"error": "Unauthorized", "message": "Invalid username or password."}
            ),
            401,
        )

    token = create_user_access_token(user)
    return jsonify(
        {
            "message": "Login successful.",
            "user": user.to_public_dict(),
            "access_token": token,
        }
    )


@auth_bp.get("/me")
@jwt_required()
@swag_from(
    {
        "tags": ["Authentication"],
        "summary": "Current user profile (JWT required)",
        "security": [{"Bearer": []}],
        "responses": {
            200: {"description": "OK"},
            401: {"description": "Missing or invalid token"},
        },
    }
)
def me():
    uid = get_current_user_id()
    user = User.query.get(uid)
    if not user:
        return jsonify({"error": "Not Found", "message": "User not found."}), 404
    return jsonify({"user": user.to_public_dict()})
