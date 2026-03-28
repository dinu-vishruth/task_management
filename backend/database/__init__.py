"""Database initialization and optional admin seeding."""
from extensions import db
from models.user_model import User


def init_db(app):
    """Create tables under application context."""
    with app.app_context():
        db.create_all()


