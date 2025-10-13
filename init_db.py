# init_db.py
from app import app, db
from models import User
import hashlib

print("🔧 Initializing PostgreSQL database...")

with app.app_context():
    try:
        db.drop_all()
        print("✓ Dropped all existing tables")

        db.create_all()
        print("✓ Created all tables successfully")

        # Create default admin
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                password=hashlib.sha256("admin123".encode()).hexdigest(),
                role="admin",
                email="admin@dispatchpro.com",
                full_name="System Administrator",
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created (admin / admin123)")
        else:
            print("✓ Admin user already exists")

        print("✅ PostgreSQL database initialization complete.")
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error initializing database: {e}")
