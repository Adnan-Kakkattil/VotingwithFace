"""
Student module - Secure voting with face recognition
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.election import Election, Candidate, Vote

student_bp = Blueprint('student', __name__, url_prefix='/student')


def student_required(f):
    """Decorator: require student role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_student():
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard - show ongoing and upcoming elections"""
    all_active = Election.query.filter(Election.is_active == True).order_by(Election.start_date.desc()).all()
    ongoing = [e for e in all_active if e.is_ongoing]
    upcoming = [e for e in all_active if e.is_upcoming]
    return render_template('student/dashboard.html', elections=ongoing, upcoming=upcoming)


@student_bp.route('/register-face')
@login_required
@student_required
def register_face_page():
    """Face registration page with webcam"""
    return render_template('student/register_face.html')


@student_bp.route('/election/<int:eid>')
@login_required
@student_required
def election_view(eid):
    """View election and candidates - option to vote or nominate"""
    election = Election.query.get_or_404(eid)
    candidates = election.candidates.filter_by(status='approved').all()
    already_voted = Vote.query.filter_by(election_id=eid, user_id=current_user.id).first() is not None
    my_nomination = Candidate.query.filter_by(election_id=eid, user_id=current_user.id).first()
    return render_template('student/election_vote.html',
        election=election,
        candidates=candidates,
        already_voted=already_voted,
        my_nomination=my_nomination
    )


@student_bp.route('/election/<int:eid>/nominate', methods=['POST'])
@login_required
@student_required
def nominate(eid):
    """Self-nominate as candidate for election"""
    election = Election.query.get_or_404(eid)
    if not election.is_ongoing and not election.is_upcoming:
        flash('Cannot nominate for completed elections.', 'error')
        return redirect(url_for('student.dashboard'))
    existing = Candidate.query.filter_by(election_id=eid, user_id=current_user.id).first()
    if existing:
        flash('You have already nominated yourself for this election.', 'info')
        return redirect(url_for('student.election_view', eid=eid))
    manifesto = request.form.get('manifesto', '').strip() if request.form else ''
    c = Candidate(election_id=eid, user_id=current_user.id, manifesto=manifesto or None, status='pending')
    db.session.add(c)
    db.session.commit()
    flash('Nomination submitted. Awaiting admin approval.', 'success')
    return redirect(url_for('student.election_view', eid=eid))
