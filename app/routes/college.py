"""
College module - Overview of elections and results
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps
from app.models.election import Election, Candidate, Vote
from app.models.user import User

college_bp = Blueprint('college', __name__, url_prefix='/college')


def college_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_college():
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@college_bp.route('/dashboard')
@login_required
@college_required
def dashboard():
    """College dashboard - all elections with status"""
    elections = Election.query.order_by(Election.start_date.desc()).all()
    return render_template('college/dashboard.html', elections=elections)


@college_bp.route('/election/<int:eid>/results')
@login_required
@college_required
def election_results(eid):
    """View election results"""
    election = Election.query.get_or_404(eid)
    results = election.get_results()
    # Get candidate details
    candidate_votes = []
    for user_id, vote_count in results:
        user = User.query.get(user_id)
        candidate = Candidate.query.filter_by(election_id=eid, user_id=user_id).first()
        if user:
            candidate_votes.append({'name': user.name, 'votes': vote_count})
    total = sum(r[1] for r in results)
    return render_template('college/results.html', election=election, candidate_votes=candidate_votes, total_votes=total)
