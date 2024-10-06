from typing import Optional
from flask import Blueprint, request, jsonify
from werkzeug.datastructures import FileStorage

from app.services.face_service import calculate_embedding

face_bp = Blueprint('face', __name__)


def allowed_file(filename: str):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@face_bp.route('/embedding', methods=['POST'])
def embedding():
    face_img: Optional[FileStorage] = request.files.get('faceImg')

    if face_img is None:
        return jsonify({'message': 'No file part'}), 400

    if not allowed_file(face_img.filename):
        return jsonify({'message': 'File type not allowed'}), 400

    try:
        embeddings = calculate_embedding(face_img)
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

    return jsonify({'embeddings': embeddings}), 200
