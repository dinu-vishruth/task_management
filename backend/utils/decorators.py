"""Auth decorators: JWT + admin role."""
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required


def admin_required(f):
    """
    Require a valid JWT and role == admin.
    Use after @jwt_required() is applied inside this decorator.
    """

    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return (
                jsonify(
                    {
                        "error": "Forbidden",
                        "message": "Administrator privileges are required for this resource.",
                    }
                ),
                403,
            )
        return f(*args, **kwargs)

    return decorated


def get_current_user_id():
    """Return authenticated user id from JWT identity."""
    ident = get_jwt_identity()
    if ident is None:
        return None
    try:
        return int(ident)
    except (TypeError, ValueError):
        return None
