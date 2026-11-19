import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.database.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agroai.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DEMO_USER_ID = "usr_ramesh_patel_01"
DEMO_USER_EMAIL = "ramesh@agrofield.ai"

def init_db():
    # Import models so Base metadata is populated
    import backend.app.models.scan
    import backend.app.models.user
    from backend.app.core.security import hash_password
    from backend.app.models.user import User
    from backend.app.models.scan import Scan

    Base.metadata.create_all(bind=engine)

    # Check and migrate users table schema if new columns are missing
    with engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(users)"))
            existing_cols = [row[1] for row in result.fetchall()]
            if "profile_photo_url" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_photo_url VARCHAR(255)"))
            if "farm_name" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN farm_name VARCHAR(150)"))
            if "main_crop" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN main_crop VARCHAR(100)"))
            if "farm_size" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN farm_size VARCHAR(50)"))
            conn.commit()
        except Exception as e:
            print(f"[Database] Users migration check: {e}")

        try:
            result = conn.execute(text("PRAGMA table_info(scans)"))
            existing_cols = [row[1] for row in result.fetchall()]
            if "user_id" not in existing_cols:
                conn.execute(text("ALTER TABLE scans ADD COLUMN user_id VARCHAR(50)"))
                conn.commit()
        except Exception as e:
            print(f"[Database] Scans migration check: {e}")

    # Ensure default demo user exists
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == DEMO_USER_EMAIL).first()
        if not demo_user:
            demo_user = User(
                id=DEMO_USER_ID,
                full_name="Ramesh Patel",
                email=DEMO_USER_EMAIL,
                password_hash=hash_password("Password123!"),
                location="Lucknow Farm, Uttar Pradesh",
                preferred_language="Hindi (HI)",
                profile_photo_url="/assets/farmer-avatar.png",
                farm_name="Patel Krishi Farm",
                main_crop="Wheat / Rice",
                farm_size="5 Acres"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
        else:
            # Ensure demo user has avatar
            if not demo_user.profile_photo_url:
                demo_user.profile_photo_url = "/assets/farmer-avatar.png"
                db.commit()

        # Assign any orphaned scans without user_id to the demo user
        db.query(Scan).filter((Scan.user_id == None) | (Scan.user_id == "")).update(
            {Scan.user_id: demo_user.id},
            synchronize_session=False
        )
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Database] Demo user init error: {e}")
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
