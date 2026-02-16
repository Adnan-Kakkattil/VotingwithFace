"""
Election, Candidate, and Vote models
"""
from datetime import datetime
from app import db


class Election(db.Model):
    """Election model"""
    __tablename__ = 'elections'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    candidates = db.relationship('Candidate', backref='election', lazy='dynamic', cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='election', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def is_ongoing(self):
        """Check if election is currently active"""
        now = datetime.utcnow()
        return self.start_date <= now <= self.end_date and self.is_active
    
    @property
    def is_upcoming(self):
        """Check if election hasn't started"""
        return datetime.utcnow() < self.start_date
    
    @property
    def is_completed(self):
        """Check if election has ended"""
        return datetime.utcnow() > self.end_date
    
    def get_results(self):
        """Get vote count per candidate"""
        from sqlalchemy import func
        return db.session.query(
            Candidate.user_id,
            func.count(Vote.id).label('vote_count')
        ).join(Vote, Vote.candidate_id == Candidate.id).filter(
            Vote.election_id == self.id
        ).group_by(Candidate.user_id).all()
    
    def __repr__(self):
        return f'<Election {self.title}>'


class Candidate(db.Model):
    """Candidate model - links users to elections"""
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manifesto = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    nominated_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    votes = db.relationship('Vote', backref='candidate', lazy='dynamic')
    
    @property
    def vote_count(self):
        return self.votes.count()
    
    def __repr__(self):
        return f'<Candidate election={self.election_id} user={self.user_id}>'


class Vote(db.Model):
    """Vote model - ensures one vote per user per election"""
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: one vote per user per election
    __table_args__ = (
        db.UniqueConstraint('election_id', 'user_id', name='unique_vote_per_election'),
    )
    
    def __repr__(self):
        return f'<Vote election={self.election_id} user={self.user_id}>'
