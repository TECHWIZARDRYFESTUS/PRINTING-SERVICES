from getpass import getpass

from . import models
from .auth import hash_password
from .database import SessionLocal


def main() -> None:
    email = input("Administrator email: ").strip().lower()
    password = getpass("New password (at least 12 characters): ")
    confirmation = getpass("Confirm new password: ")

    if len(password) < 12:
        raise SystemExit("Password must contain at least 12 characters.")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    db = SessionLocal()
    try:
        account = db.query(models.User).filter_by(email=email, role="admin").first()
        if not account:
            raise SystemExit("No administrator account found with that email.")
        account.password_hash = hash_password(password)
        db.add(models.AuditLog(
            action="admin.password_reset",
            details=f"user_id={account.id}",
        ))
        db.commit()
        print(f"Password reset for administrator {email}. Sign in with your new password.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
