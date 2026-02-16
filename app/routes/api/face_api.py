"""
Face recognition API - used for registration and verification
"""
import base64
import io
import numpy as np
import cv2
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

face_api_bp = Blueprint('face_api', __name__, url_prefix='/api/face')


def get_face_service():
    from flask import current_app
    from app.services.face_recognition_service import FaceRecognitionService
    return FaceRecognitionService(
        current_app.config['FACE_ENCODINGS_FOLDER'],
        tolerance=getattr(
            current_app.config.get('FACE_ENCODING_TOLERANCE', 0.5),
            0.5
        )
    )


def decode_image_from_request():
    """Decode image from base64 or file upload"""
    if request.form.get('image'):
        # Base64 data URL or raw base64
        data = request.form['image']
        if ',' in data:
            data = data.split(',')[1]
        img_bytes = base64.b64decode(data)
    elif request.files.get('image'):
        img_bytes = request.files['image'].read()
    else:
        return None
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


@face_api_bp.route('/register', methods=['POST'])
@login_required
def register_face():
    """
    Register user's face. Expects multipart form with 'image' (file or base64).
    Students only.
    """
    if not current_user.is_student():
        return jsonify({'success': False, 'error': 'Students only'}), 403
    
    img = decode_image_from_request()
    if img is None:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
    
    service = get_face_service()
    if not service.detect_face_in_image(img):
        return jsonify({
            'success': False,
            'error': 'Ensure exactly one face is visible in the frame'
        }), 400
    
    encoding = service.encode_face_from_image(img)
    if encoding is None:
        return jsonify({'success': False, 'error': 'Could not extract face encoding'}), 400
    
    path = service.save_encoding(current_user.id, encoding)
    current_user.face_encoding_path = path
    from app import db
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Face registered successfully'})


@face_api_bp.route('/verify', methods=['POST'])
@login_required
def verify_face():
    """
    Verify user's face against stored encoding.
    Returns success if face matches.
    """
    if not current_user.is_student():
        return jsonify({'success': False, 'error': 'Students only'}), 403
    
    if not current_user.face_encoding_path:
        return jsonify({'success': False, 'error': 'No face registered'}), 400
    
    img = decode_image_from_request()
    if img is None:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
    
    service = get_face_service()
    encoding = service.encode_face_from_image(img)
    if encoding is None:
        return jsonify({'success': False, 'error': 'Could not detect face'}), 400
    
    match, distance = service.verify_face(encoding, current_user.face_encoding_path)
    return jsonify({
        'success': match,
        'verified': match,
        'distance': distance
    })
