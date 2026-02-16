"""
College Voting System - Flask Application Factory
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['FACE_ENCODINGS_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)
    
    from app.routes.student import student_bp
    app.register_blueprint(student_bp)
    
    from app.routes.college import college_bp
    app.register_blueprint(college_bp)
    
    from app.routes.candidate import candidate_bp
    app.register_blueprint(candidate_bp)
    
    from app.routes.api.face_api import face_api_bp
    app.register_blueprint(face_api_bp)
    from app.routes.api.vote_api import vote_api_bp
    app.register_blueprint(vote_api_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
