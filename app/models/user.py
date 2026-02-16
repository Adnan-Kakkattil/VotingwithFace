"""
User model - supports Admin, Student, College, Candidate roles
"""
from datetime import datetime
from flask_login import UserMixin
from app import db
import bcrypt


class User(UserMixin, db.Model):
    """User model with role-based access"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, student, college, candidate
    student_id = db.Column(db.String(20), unique=True, nullable=True)  # For students
    department = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    face_encoding_path = db.Column(db.String(255), nullable=True)  # Path to stored face encoding
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    votes = db.relationship('Vote', backref='voter', lazy='dynamic')
    candidacies = db.relationship('Candidate', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_student(self):
        return self.role == 'student'
    
    def is_college(self):
        return self.role == 'college'
    
    def is_candidate(self):
        return self.role == 'candidate'
    
    def has_face_registered(self):
        """Check if user has registered face encoding for voting"""
        return bool(self.face_encoding_path)
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
