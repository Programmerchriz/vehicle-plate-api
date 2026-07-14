from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.config.security import hash_password
from app.models.enums import UserRole
from app.models.user import User


ADMIN_EMAIL = "admin@vehicleplate.com"
ADMIN_PASSWORD = "Admin123!"
ADMIN_NAME = "System Administrator"


def seed_admin():
  db: Session = SessionLocal()

  try:
    existing_admin = (
      db.query(User)
      .filter(User.email == ADMIN_EMAIL)
      .first()
    )

    if existing_admin:
      print("✅ Admin user already exists.")
      return

    admin = User(
      full_name=ADMIN_NAME,
      email=ADMIN_EMAIL,
      password_hash=hash_password(ADMIN_PASSWORD),
      role=UserRole.ADMIN,
      is_active=True,
    )

    db.add(admin)
    db.commit()

    print("✅ Admin user created successfully!")
    print(f"Email: {ADMIN_EMAIL}")
    print(f"Password: {ADMIN_PASSWORD}")

  finally:
    db.close()


if __name__ == "__main__":
  seed_admin()