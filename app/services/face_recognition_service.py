"""
Face Recognition Service - Registration and verification for voting
Uses face_recognition library (dlib-based) for face encoding and matching
"""
import os
import pickle
import numpy as np

try:
    import face_recognition
    import cv2
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


class FaceRecognitionService:
    """Handle face encoding, storage, and verification"""
    
    def __init__(self, encodings_folder, tolerance=0.5):
        self.encodings_folder = encodings_folder
        self.tolerance = tolerance
        os.makedirs(encodings_folder, exist_ok=True)
    
    def _get_encoding_path(self, user_id):
        """Get file path for user's face encoding"""
        return os.path.join(self.encodings_folder, f"user_{user_id}.pkl")
    
    def encode_face_from_image(self, image_array):
        """
        Extract face encoding from image (numpy array, BGR from OpenCV)
        Returns encoding as list or None if no face/multiple faces
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return None
        try:
            # face_recognition expects RGB
            rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb)
            if len(encodings) == 1:
                return encodings[0].tolist()
            return None
        except Exception:
            return None
    
    def encode_face_from_file(self, file_path):
        """Extract face encoding from image file path"""
        if not FACE_RECOGNITION_AVAILABLE:
            return None
        try:
            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)
            if len(encodings) == 1:
                return encodings[0].tolist()
            return None
        except Exception:
            return None
    
    def save_encoding(self, user_id, encoding):
        """Save face encoding to disk"""
        path = self._get_encoding_path(user_id)
        with open(path, 'wb') as f:
            pickle.dump(encoding, f)
        return path
    
    def load_encoding(self, user_id_or_path):
        """Load face encoding - accepts user_id (int) or file path (str)"""
        if isinstance(user_id_or_path, str) and user_id_or_path.endswith('.pkl'):
            path = user_id_or_path
        else:
            path = self._get_encoding_path(user_id_or_path)
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    
    def verify_face(self, unknown_encoding, user_id_or_path):
        """
        Verify if unknown face matches stored encoding.
        Returns (success: bool, distance: float or None)
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return False, None
        stored = self.load_encoding(user_id_or_path)
        if stored is None or unknown_encoding is None:
            return False, None
        try:
            unknown = np.array(unknown_encoding)
            stored_arr = np.array(stored)
            # face_recognition.face_distance returns array of distances
            distance = face_recognition.face_distance([stored_arr], unknown)[0]
            match = distance <= self.tolerance
            return match, float(distance)
        except Exception:
            return False, None
    
    def detect_face_in_image(self, image_array):
        """Check if exactly one face is present in image"""
        if not FACE_RECOGNITION_AVAILABLE:
            return False
        try:
            rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb)
            return len(face_locations) == 1
        except Exception:
            return False
    
    def delete_encoding(self, user_id):
        """Remove stored face encoding for user"""
        path = self._get_encoding_path(user_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
