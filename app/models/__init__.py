"""
Database models for College Voting System
"""
from app.models.user import User
from app.models.election import Election, Candidate, Vote

__all__ = ['User', 'Election', 'Candidate', 'Vote']
