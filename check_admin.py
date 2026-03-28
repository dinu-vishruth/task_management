
import os
import sys
from pathlib import Path

# Add backend to path
_root = Path(__file__).resolve().parent / "backend"
sys.path.append(str(_root))

from app import create_app
from extensions import db
from models.user_model import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print("Users in database:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}")
