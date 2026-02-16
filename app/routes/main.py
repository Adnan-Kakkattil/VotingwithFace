"""
Main routes - Dashboard, Home
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Role-based dashboard redirect"""
    if current_user.is_admin():
        return redirect(url_for('admin.index'))
    if current_user.is_student():
        return redirect(url_for('student.dashboard'))
    if current_user.is_college():
        return redirect(url_for('college.dashboard'))
    if current_user.is_candidate():
        return redirect(url_for('candidate.dashboard'))
    return redirect(url_for('main.index'))
