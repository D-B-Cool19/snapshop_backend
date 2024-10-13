import json
import os
import uuid
from typing import Optional, List
from flask import Blueprint, request, jsonify, url_for, current_app
from flask_jwt_extended import create_access_token
from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from ..models.user import User
from ..services.face_service import cosine_similarity
from ..services.user_service import create_user

user_bp = Blueprint('user', __name__)


def allowed_file(filename: str):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@user_bp.route('/register', methods=['POST'])
def register():
    class UserDataModel(BaseModel):
        username: str = Field(..., min_length=4, max_length=20,
                              description='Username must be between 4 and 20 characters')
        email: EmailStr
        password: str = Field(..., min_length=8, max_length=50,
                              description='Password must be between 8 and 50 characters')
        gender: str = Field(..., pattern='^(male|female|unknown)$',
                            description='Gender must be either \'male\', \'female\', or \'unknown\'')
        age: Optional[int] = Field(None, ge=1, le=120, description='Age must be between 1 and 120')
        embedding: Optional[List[float]] = Field(None, min_length=512, max_length=512)

        @field_validator('age', mode='before')
        def convert_age(cls, value):
            if value is None or value == '':
                return None
            if isinstance(value, str) and value.isdigit():
                return int(value)
            if isinstance(value, int):
                return value
            raise ValueError('Age must be a valid integer')

        @field_validator('embedding', mode='before')
        def convert_embedding(cls, value):
            if value is None or value == '':
                return None
            else:
                return json.loads(value)

    try:
        data = UserDataModel(**request.form)
    except ValidationError as e:
        return jsonify({'message': 'Invalid input', 'errors': e.errors()}), 400

    username = data.username
    password = data.password
    email = data.email
    gender = data.gender
    age = data.age
    face_img: Optional[FileStorage] = request.files.get('faceImg')
    embedding: Optional[List[float]] = data.embedding

    try:
        if User.query.filter_by(username=username).first() is not None:
            return jsonify({'message': 'User already exists'}), 400

        if User.query.filter_by(email=email).first() is not None:
            return jsonify({'message': 'Email already exists'}), 400

        face_img_url: Optional[str] = None
        if face_img:
            if not allowed_file(face_img.filename):
                return jsonify({'message': 'File type not allowed'}), 400

            file_ext = os.path.splitext(secure_filename(face_img.filename))[1]
            filename = f'{uuid.uuid4().hex}{file_ext}'
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            face_img_url = url_for('static', filename=f'uploads/{filename}', _external=True)
            try:
                if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
                    os.makedirs(current_app.config['UPLOAD_FOLDER'])
                face_img.save(file_path)
                if not embedding:
                    return jsonify({'message': 'Face embedding is required'}), 400
            except Exception as e:
                return jsonify({'message': f'An error occurred: {str(e)}'}), 500

        new_user = create_user(
            username=username,
            email=email,
            password=password,
            gender=gender,
            age=age,
            face_img_url=face_img_url,
            embedding=embedding
        )

    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

    return jsonify({'user': new_user.to_dict()}), 201


@user_bp.route('/available/username/<username>', methods=['GET'])
def is_username_available(username: str):
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'available': False}), 200
    return jsonify({'available': True}), 200


@user_bp.route('/available/email/<email>', methods=['GET'])
def is_email_available(email: str):
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'available': False}), 200
    return jsonify({'available': True}), 200


@user_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 400
    access_token = create_access_token(identity=user.to_dict())
    return jsonify({
        'user': user.to_dict(),
        'token': access_token
    }), 200


@user_bp.route('/query', methods=['POST'])
def login_with_face():
    embedding = request.json.get('embedding')
    users = User.query.all()
    similar_users: List[User] = []

    for user in users:
        if user.embedding is None:
            continue
        similarity = cosine_similarity(embedding, user.embedding)
        if similarity > 0.5:
            similar_users.append(user)

    if len(similar_users) == 0:
        return jsonify({'message': 'No similar users found'}), 400

    similar_users_list = [user.to_public_dict() for user in similar_users]
    if len(similar_users) > 1:
        return jsonify({'similarUsers': similar_users_list}), 200

    login_info = {
        'user': similar_users[0].to_dict(),
        'token': create_access_token(identity=similar_users[0].to_dict())
    }
    return jsonify({'loginInfo': login_info}), 200
