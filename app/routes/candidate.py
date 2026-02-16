"""
Candidate module - Nomination status and election statistics
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps
from app.models.election import Candidate

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')


def candidate_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_candidate():
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@candidate_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Candidate dashboard - show candidacies for current user.
    Accessible to users with role 'candidate' OR users who have any Candidate record.
    """
    # Allow if role is candidate OR user has candidacies (e.g. student who nominated)
    if not current_user.is_candidate() and not current_user.candidacies.count():
        from flask import redirect, url_for
        return redirect(url_for('main.dashboard'))
    
    candidacies = current_user.candidacies.order_by(Candidate.nominated_at.desc()).all()
    return render_template('candidate/dashboard.html', candidacies=candidacies)
