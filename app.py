from flask import Flask, redirect, url_for
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    
    # Session configuration to ensure sessions persist
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = True if os.getenv('DATABASE_URL') else False
    app.config['SESSION_COOKIE_NAME'] = 'resume_analyzer_session'
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Refresh session on each request

    from extensions import db
    db.init_app(app)

    # Import and register blueprints
    from auth import auth_bp
    from resume import resume_bp
    from dashboard import dashboard_bp
    from linkedin import linkedin_bp
    from test_bp import test_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(linkedin_bp, url_prefix='/linkedin')
    app.register_blueprint(test_bp, url_prefix='/test')

    # Root route - redirect to login
    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from extensions import db
        db.create_all()
    app.run(debug=True)