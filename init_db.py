from app import app, db
from models import User
import hashlib

print("Initializing database...")

with app.app_context():
    try:
        # Drop all tables first (optional - only if you want fresh start)
        db.drop_all()
        print("✓ Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Create admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=hashlib.sha256('admin123'.encode()).hexdigest(),
                role='admin',
                email='admin@dispatchpro.com',
                full_name='System Administrator'
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created")
        else:
            print("✓ Admin user already exists")
        
        print("\n" + "="*50)
        print("Setup Complete!")
        print("="*50)
        print("\nLogin Credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n⚠️  Change password after first login!")
        print("\nStart app: python app.py")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.session.rollback()