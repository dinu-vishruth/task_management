"""Input validation helpers — keep rules in one place."""
import re
from typing import Optional, Tuple

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,80}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_username(username: Optional[str]) -> Tuple[bool, str]:
    if not username or not isinstance(username, str):
        return False, "Username is required."
    username = username.strip()
    if not USERNAME_PATTERN.match(username):
        return False, "Username must be 3–80 characters (letters, digits, underscore)."
    return True, username


def validate_email(email: Optional[str]) -> Tuple[bool, str]:
    if not email or not isinstance(email, str):
        return False, "Email is required."
    email = email.strip().lower()
    if len(email) > 120 or not EMAIL_PATTERN.match(email):
        return False, "Invalid email format."
    return True, email


def validate_password(password: Optional[str]) -> Tuple[bool, str]:
    if not password or not isinstance(password, str):
        return False, "Password is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if len(password) > 128:
        return False, "Password is too long."
    return True, password


def validate_task_title(title: Optional[str]) -> Tuple[bool, str]:
    if not title or not isinstance(title, str):
        return False, "Title is required."
    title = title.strip()
    if not title:
        return False, "Title cannot be empty."
    if len(title) > 200:
        return False, "Title must be at most 200 characters."
    return True, title


def sanitize_description(description) -> str:
    if description is None:
        return ""
    if not isinstance(description, str):
        return ""
    return description.strip()[:5000]
