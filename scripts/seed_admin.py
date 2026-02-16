"""
Seed initial users for development
Run from project root: python -m scripts.seed_admin
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User


def seed_users():
    app = create_app('development')
    with app.app_context():
        # Admin
        if not User.query.filter_by(email='admin@college.edu').first():
            admin = User(email='admin@college.edu', name='Admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print('Admin: admin@college.edu / admin123')
        
        # College user
        if not User.query.filter_by(email='college@college.edu').first():
            college = User(email='college@college.edu', name='College Admin', role='college')
            college.set_password('college123')
            db.session.add(college)
            print('College: college@college.edu / college123')
        
        # Sample student
        if not User.query.filter_by(email='student@college.edu').first():
            student = User(email='student@college.edu', name='John Student', role='student', student_id='S001')
            student.set_password('student123')
            db.session.add(student)
            print('Student: student@college.edu / student123')
        
        db.session.commit()
        print('Done. Change passwords after first login!')


if __name__ == '__main__':
    seed_users()
