"""Task model — owned by a user (created_by)."""
from datetime import datetime, timezone

from extensions import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    is_global = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self, include_author=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_by": self.user_id,
            "is_global": self.is_global,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_author and self.author:
            data["author_username"] = self.author.username
        return data
