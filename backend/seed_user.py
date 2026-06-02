from core.database import SessionLocal
from models.models import User, RoleEnum
from core.security import get_password_hash

def seed_user():
    db = SessionLocal()
    try:
        # Check if user exists
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            admin_user = User(
                username="admin",
                email="admin@qainspect.pro",
                hashed_password=get_password_hash("admin123"),
                role=RoleEnum.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created: admin / admin123")
        else:
            print("Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_user()
