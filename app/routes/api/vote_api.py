"""
Vote API - Cast vote with face verification
"""
import base64
import io
import numpy as np
import cv2
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.election import Election, Candidate, Vote

vote_api_bp = Blueprint('vote_api', __name__, url_prefix='/api/vote')


def get_face_service():
    from flask import current_app
    from app.services.face_recognition_service import FaceRecognitionService
    return FaceRecognitionService(
        current_app.config['FACE_ENCODINGS_FOLDER'],
        tolerance=current_app.config.get('FACE_ENCODING_TOLERANCE', 0.5)
    )


def decode_image_from_request():
    if request.form.get('image'):
        data = request.form['image']
        if ',' in data:
            data = data.split(',')[1]
        img_bytes = base64.b64decode(data)
    elif request.files.get('image'):
        img_bytes = request.files['image'].read()
    else:
        return None
    nparr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


@vote_api_bp.route('/cast', methods=['POST'])
@login_required
def cast_vote():
    """
    Cast vote: requires face image for verification, candidate_id, election_id.
    """
    if not current_user.is_student():
        return jsonify({'success': False, 'error': 'Students only'}), 403

    if not current_user.has_face_registered():
        return jsonify({'success': False, 'error': 'Register your face first'}), 400

    election_id = request.form.get('election_id', type=int)
    candidate_id = request.form.get('candidate_id', type=int)
    if not election_id or not candidate_id:
        return jsonify({'success': False, 'error': 'election_id and candidate_id required'}), 400

    election = Election.query.get(election_id)
    if not election or not election.is_ongoing:
        return jsonify({'success': False, 'error': 'Election not active'}), 400

    candidate = Candidate.query.filter_by(id=candidate_id, election_id=election_id, status='approved').first()
    if not candidate:
        return jsonify({'success': False, 'error': 'Invalid candidate'}), 400

    if Vote.query.filter_by(election_id=election_id, user_id=current_user.id).first():
        return jsonify({'success': False, 'error': 'You have already voted'}), 400

    # Face verification
    img = decode_image_from_request()
    if img is None:
        return jsonify({'success': False, 'error': 'No image provided'}), 400

    service = get_face_service()
    encoding = service.encode_face_from_image(img)
    if encoding is None:
        return jsonify({'success': False, 'error': 'Could not detect face'}), 400

    match, _ = service.verify_face(encoding, current_user.face_encoding_path)
    if not match:
        return jsonify({'success': False, 'error': 'Face verification failed'}), 403

    vote = Vote(election_id=election_id, candidate_id=candidate_id, user_id=current_user.id)
    db.session.add(vote)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Vote cast successfully'})
