"""Task CRUD — users own tasks; admins can access all."""
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask_jwt_extended import get_jwt, jwt_required

from extensions import db
from models.task_model import Task
from models.user_model import User
from utils.decorators import get_current_user_id
from utils.validation import sanitize_description, validate_task_title

task_bp = Blueprint("tasks", __name__)


def _is_admin():
    return get_jwt().get("role") == "admin"


def _can_access_task(task, write_access=False):
    """
    Check if the current user can access a task.
    Admins can always access and modify any task.
    Users can always view their own tasks and global tasks.
    Users can ONLY modify their own tasks.
    """
    if _is_admin():
        return True

    uid = get_current_user_id()
    if uid is None:
        return False

    # If it's a global task, regular users can view it but NOT modify it.
    if task.is_global:
        return not write_access

    # Otherwise, it must be the user's own task.
    return task.user_id == uid


@task_bp.post("")
@jwt_required()
@swag_from(
    {
        "tags": ["Tasks"],
        "summary": "Create a task",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "required": ["title"],
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                    },
                },
            }
        ],
        "responses": {
            201: {"description": "Created"},
            400: {"description": "Validation error"},
            401: {"description": "Unauthorized"},
        },
    }
)
def create_task():
    data = request.get_json(silent=True) or {}
    ok, title = validate_task_title(data.get("title"))
    if not ok:
        return jsonify({"error": "Bad Request", "message": title}), 400
    description = sanitize_description(data.get("description"))

    uid = get_current_user_id()
    user = User.query.get(uid)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Invalid user."}), 401

    is_global = _is_admin()
    task = Task(title=title, description=description, user_id=uid, is_global=is_global)
    db.session.add(task)
    db.session.commit()
    return (
        jsonify(
            {
                "message": "Task created.",
                "task": task.to_dict(include_author=_is_admin()),
            }
        ),
        201,
    )


@task_bp.get("")
@jwt_required()
@swag_from(
    {
        "tags": ["Tasks"],
        "summary": "List tasks (own tasks, or all structured if admin)",
        "security": [{"Bearer": []}],
        "responses": {
            200: {"description": "OK"},
            401: {"description": "Unauthorized"},
        },
    }
)
def list_tasks():
    if _is_admin():
        all_tasks = Task.query.order_by(Task.created_at.desc()).all()
        admin_tasks = [t.to_dict(include_author=True) for t in all_tasks if t.is_global]
        user_tasks = [t.to_dict(include_author=True) for t in all_tasks if not t.is_global]
        return jsonify({
            "admin_tasks": admin_tasks,
            "user_tasks": user_tasks,
            "is_admin": True,
            "count": len(all_tasks)
        })
    else:
        uid = get_current_user_id()
        tasks = (
            Task.query.filter((Task.user_id == uid) | (Task.is_global == True))
            .order_by(Task.created_at.desc())
            .all()
        )
        return jsonify({
            "tasks": [t.to_dict(include_author=False) for t in tasks],
            "is_admin": False,
            "count": len(tasks)
        })


@task_bp.put("/<int:task_id>")
@jwt_required()
@swag_from(
    {
        "tags": ["Tasks"],
        "summary": "Update a task",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "required": True,
            },
            {
                "name": "body",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                    },
                },
            },
        ],
        "responses": {
            200: {"description": "OK"},
            403: {"description": "Forbidden"},
            404: {"description": "Not found"},
        },
    }
)
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Not Found", "message": "Task not found."}), 404
    if not _can_access_task(task, write_access=True):
        msg = "Administrators' global tasks are read-only." if task.is_global else "You can only modify your own tasks."
        return (
            jsonify({"error": "Forbidden", "message": msg}),
            403,
        )

    data = request.get_json(silent=True) or {}
    if "title" in data:
        ok, title = validate_task_title(data.get("title"))
        if not ok:
            return jsonify({"error": "Bad Request", "message": title}), 400
        task.title = title
    if "description" in data:
        task.description = sanitize_description(data.get("description"))

    db.session.commit()
    return jsonify(
        {
            "message": "Task updated.",
            "task": task.to_dict(include_author=_is_admin()),
        }
    )


@task_bp.delete("/<int:task_id>")
@jwt_required()
@swag_from(
    {
        "tags": ["Tasks"],
        "summary": "Delete a task",
        "security": [{"Bearer": []}],
        "parameters": [
            {
                "name": "task_id",
                "in": "path",
                "type": "integer",
                "required": True,
            }
        ],
        "responses": {
            200: {"description": "OK"},
            403: {"description": "Forbidden"},
            404: {"description": "Not found"},
        },
    }
)
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Not Found", "message": "Task not found."}), 404
    if not _can_access_task(task, write_access=True):
        msg = "Administrators' global tasks are read-only." if task.is_global else "You can only delete your own tasks."
        return (
            jsonify({"error": "Forbidden", "message": msg}),
            403,
        )

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted."})
