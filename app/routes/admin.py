"""
Admin module - Manages elections, candidates, student access, system monitoring
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.election import Election, Candidate, Vote

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    elections = Election.query.order_by(Election.created_at.desc()).all()
    total_students = User.query.filter_by(role='student').count()
    total_votes = Vote.query.count()
    pending_candidates = Candidate.query.filter_by(status='pending').count()
    return render_template('admin/dashboard.html',
        elections=elections,
        total_students=total_students,
        total_votes=total_votes,
        pending_candidates=pending_candidates
    )


@admin_bp.route('/elections')
@login_required
@admin_required
def elections_list():
    elections = Election.query.order_by(Election.created_at.desc()).all()
    return render_template('admin/elections.html', elections=elections)


@admin_bp.route('/elections/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_election():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        start = request.form.get('start_date')
        end = request.form.get('end_date')
        if not title or not start or not end:
            flash('Title and dates are required.', 'error')
            return render_template('admin/election_form.html')
        try:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        except ValueError:
            start_dt = datetime.strptime(start, '%Y-%m-%dT%H:%M')
            end_dt = datetime.strptime(end, '%Y-%m-%dT%H:%M')
        if start_dt >= end_dt:
            flash('End date must be after start date.', 'error')
            return render_template('admin/election_form.html')
        election = Election(
            title=title,
            description=description or None,
            start_date=start_dt,
            end_date=end_dt,
            created_by=current_user.id
        )
        db.session.add(election)
        db.session.commit()
        flash('Election created successfully.', 'success')
        return redirect(url_for('admin.elections_list'))
    return render_template('admin/election_form.html')


@admin_bp.route('/elections/<int:eid>')
@login_required
@admin_required
def election_detail(eid):
    election = Election.query.get_or_404(eid)
    candidates = election.candidates.all()
    return render_template('admin/election_detail.html', election=election, candidates=candidates)


@admin_bp.route('/elections/<int:eid>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_election(eid):
    election = Election.query.get_or_404(eid)
    election.is_active = not election.is_active
    db.session.commit()
    flash(f'Election {"activated" if election.is_active else "deactivated"}.', 'success')
    return redirect(request.referrer or url_for('admin.elections_list'))


@admin_bp.route('/candidates')
@login_required
@admin_required
def candidates_list():
    candidates = Candidate.query.join(User).order_by(Candidate.nominated_at.desc()).all()
    return render_template('admin/candidates.html', candidates=candidates)


@admin_bp.route('/candidates/<int:cid>/approve', methods=['POST'])
@login_required
@admin_required
def approve_candidate(cid):
    c = Candidate.query.get_or_404(cid)
    c.status = 'approved'
    c.approved_at = datetime.utcnow()
    db.session.commit()
    flash('Candidate approved.', 'success')
    return redirect(request.referrer or url_for('admin.candidates_list'))


@admin_bp.route('/candidates/<int:cid>/reject', methods=['POST'])
@login_required
@admin_required
def reject_candidate(cid):
    c = Candidate.query.get_or_404(cid)
    c.status = 'rejected'
    db.session.commit()
    flash('Candidate rejected.', 'info')
    return redirect(request.referrer or url_for('admin.candidates_list'))


@admin_bp.route('/students')
@login_required
@admin_required
def students_list():
    students = User.query.filter_by(role='student').order_by(User.name).all()
    return render_template('admin/students.html', students=students)


@admin_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        student_id = request.form.get('student_id', '').strip() or None
        department = request.form.get('department', '').strip() or None
        if not email or not name or not password:
            flash('Email, name and password are required.', 'error')
            return render_template('admin/user_form.html', role='student')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('admin/user_form.html', role='student')
        u = User(email=email, name=name, role='student', student_id=student_id, department=department)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash(f'Student {name} added successfully.', 'success')
        return redirect(url_for('admin.students_list'))
    return render_template('admin/user_form.html', role='student')


@admin_bp.route('/users/<int:uid>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(uid):
    u = User.query.get_or_404(uid)
    if u.is_admin():
        flash('Cannot deactivate admin.', 'error')
        return redirect(request.referrer or url_for('admin.index'))
    u.is_active = not u.is_active
    db.session.commit()
    flash(f'User {"activated" if u.is_active else "deactivated"}.', 'success')
    return redirect(request.referrer or url_for('admin.students_list'))
