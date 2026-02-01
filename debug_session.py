"""Debug script to check database and session configuration"""
from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    # Check if database has any users
    users = User.query.all()
    print(f"\n=== Database Check ===")
    print(f"Total users in database: {len(users)}")
    for user in users:
        print(f"  - Username: {user.username}, ID: {user.id}")
    
    # Check Flask configuration
    print(f"\n=== Flask Session Config ===")
    print(f"SECRET_KEY set: {bool(app.config.get('SECRET_KEY'))}")
    print(f"SECRET_KEY value: {app.config.get('SECRET_KEY')[:20]}...")
    print(f"SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
    print(f"PERMANENT_SESSION_LIFETIME: {app.config.get('PERMANENT_SESSION_LIFETIME')}")
    print(f"SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY')}")
    print(f"SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE')}")
    
    print("\n=== Database Path ===")
    print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    if len(users) == 0:
        print("\n⚠️  WARNING: No users found in database!")
        print("You need to register a user first before you can log in.")
    else:
        print("\n✅ Users exist in database. Login should work.")
