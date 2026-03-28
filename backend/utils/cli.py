"""Flask CLI commands for professional user and admin management."""
import click
from flask.cli import AppGroup
from werkzeug.security import generate_password_hash

from extensions import db
from models.user_model import User
from utils.validation import validate_email, validate_password, validate_username

admin_cli = AppGroup("admin", help="Professional user management commands.")


@admin_cli.command("create")
@click.option("--username", prompt="Username", help="The username for the new admin.")
@click.option("--email", prompt="Email", help="The email for the new admin.")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="The password for the new admin.")
def create_admin(username, email, password):
    """Create a new administrator account interactively."""
    username = username.strip()
    email = email.strip()

    # Validation
    ok, msg = validate_username(username)
    if not ok:
        click.echo(f"Error: {msg}")
        return

    ok, msg = validate_email(email)
    if not ok:
        click.echo(f"Error: {msg}")
        return

    ok, msg = validate_password(password)
    if not ok:
        click.echo(f"Error: {msg}")
        return

    if User.query.filter((User.username == username) | (User.email == email)).first():
        click.echo("Error: A user with that username or email already exists.")
        return

    admin = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role="admin",
    )
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Successfully created admin user: {username}")


@admin_cli.command("promote")
@click.argument("username")
def promote_user(username):
    """Promote an existing user to the 'admin' role."""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f"Error: User '{username}' not found.")
        return

    if user.role == "admin":
        click.echo(f"User '{username}' is already an admin.")
        return

    user.role = "admin"
    db.session.commit()
    click.echo(f"Successfully promoted '{username}' to admin.")


@admin_cli.command("reset-password")
@click.argument("username")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def reset_password(username, password):
    """Securely reset a user's password from the command line."""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f"Error: User '{username}' not found.")
        return

    ok, msg = validate_password(password)
    if not ok:
        click.echo(f"Error: {msg}")
        return

    user.password_hash = generate_password_hash(password)
    db.session.commit()
    click.echo(f"Password reset successfully for user: {username}")


@admin_cli.command("list")
def list_admins():
    """List all administrative accounts."""
    admins = User.query.filter_by(role="admin").all()
    if not admins:
        click.echo("No administrators found.")
        return

    click.echo(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Created At'}")
    click.echo("-" * 70)
    for a in admins:
        created = a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else "N/A"
        click.echo(f"{a.id:<5} {a.username:<20} {a.email:<30} {created}")
