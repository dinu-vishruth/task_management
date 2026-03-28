"""JWT access token helpers."""
from flask_jwt_extended import create_access_token


def create_user_access_token(user):
    """Build JWT with user id as identity and role in claims."""
    return create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "username": user.username,
        },
    )


def parse_user_id(identity_str):
    """Convert JWT identity string to int user id."""
    try:
        return int(identity_str)
    except (TypeError, ValueError):
        return None
