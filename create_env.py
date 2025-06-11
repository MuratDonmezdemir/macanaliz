import os
import secrets
from typing import Optional, Dict


def generate_secret_key() -> str:
    """Generate a secure random secret key."""
    return secrets.token_hex(32)


def create_env_file(
    flask_app: str = "run.py",
    flask_env: str = "development",
    secret_key: Optional[str] = None,
    db_url: str = "sqlite:///windsurf.db",
    force: bool = False,
) -> None:
    """
    Create or update a .env file with the specified configuration.

    Args:
        flask_app: The Flask application entry point
        flask_env: The Flask environment (development/production)
        secret_key: Optional secret key (will be generated if not provided)
        db_url: Database connection URL
        force: If True, overwrite existing .env file without confirmation
    """
    env_path = ".env"

    # Check if .env exists and get user confirmation before overwriting
    if os.path.exists(env_path) and not force:
        response = input(
            "Warning: .env file already exists. Overwrite? (y/n): "
        ).lower()
        if response != "y":
            print("Operation cancelled.")
            return

    # Generate secret key if not provided
    if not secret_key:
        secret_key = generate_secret_key()

    # Prepare environment variables
    env_vars = {
        "# Flask Configuration": "",
        "FLASK_APP": flask_app,
        "FLASK_ENV": flask_env,
        "SECRET_KEY": secret_key,
        "": "",
        "# Database": "",
        "DATABASE_URL": db_url,
    }

    # Format environment variables
    env_content = "\n".join(
        f"{key}={value}" if key and not key.startswith("#") else key
        for key, value in env_vars.items()
        if key or value
    )

    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)
        print(f"✓ {env_path} file created/updated successfully")
        print(
            "   Please keep your SECRET_KEY secure and do not commit it to version control!"
        )
    except IOError as e:
        print(f"✗ Error creating {env_path}: {e}")
        return False

    return True


def main() -> None:
    """Main function to handle command-line execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Create or update .env file")
    parser.add_argument("--app", default="run.py", help="Flask application entry point")
    parser.add_argument(
        "--env",
        default="development",
        choices=["development", "production"],
        help="Flask environment",
    )
    parser.add_argument("--db", default="sqlite:///windsurf.db", help="Database URL")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .env without confirmation",
    )

    args = parser.parse_args()

    create_env_file(
        flask_app=args.app, flask_env=args.env, db_url=args.db, force=args.force
    )


if __name__ == "__main__":
    main()
