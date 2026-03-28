"""Admin-only user management."""
from flask import Blueprint, jsonify
from flasgger import swag_from

from extensions import db
from models.user_model import User
from utils.decorators import admin_required, get_current_user_id

admin_bp = Blueprint("admin_users", __name__)


@admin_bp.get("")
@admin_required
@swag_from(
    {
        "tags": ["Admin"],
        "summary": "List all users (admin only)",
        "security": [{"Bearer": []}],
        "responses": {
            200: {"description": "OK"},
            403: {"description": "Forbidden"},
        },
    }
)
def list_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify(
        {"users": [u.to_public_dict() for u in users], "count": len(users)}
    )


@admin_bp.delete("/<int:user_id>")
@admin_required
@swag_from(
    {
        "tags": ["Admin"],
        "summary": "Delete a user (admin only; cannot delete self)",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "integer",
                "required": True,
            }
        ],
        "responses": {
            200: {"description": "OK"},
            400: {"description": "Bad request"},
            403: {"description": "Forbidden"},
            404: {"description": "Not found"},
        },
    }
)
def delete_user(user_id):
    current_id = get_current_user_id()
    if current_id == user_id:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "You cannot delete your own account via this endpoint.",
                }
            ),
            400,
        )

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Not Found", "message": "User not found."}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted."})
