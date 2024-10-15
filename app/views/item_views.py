import os
import uuid
from typing import Optional, List
from flask import Blueprint, request, jsonify, url_for, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import BaseModel, Field, ValidationError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from ..models.user import User
from ..models.item import Item
from ..services.item_service import create_item, update_item, delete_item

item_bp = Blueprint('item', __name__)


class ItemDataModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100,
                                description='Name must be between 1 and 100 characters')
    description: Optional[str] = Field(None, max_length=500,
                                       description='Description must be less than 500 characters')
    features: Optional[str] = Field(None, max_length=500,
                                    description='Feature must be less than 500 characters')
    price: Optional[float] = Field(None, gt=0, description='Price must be greater than 0')


def allowed_file(filename: str):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def upload_image(image: FileStorage):
    file_ext = os.path.splitext(secure_filename(image.filename))[1]
    filename = f'{uuid.uuid4().hex}{file_ext}'
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    return url_for('static', filename=f'uploads/{filename}')


def check_user_permission():
    current_user = get_jwt_identity()
    user: Optional[User] = User.query.get(current_user['id'])
    return user and user.role == 1


@item_bp.route('', methods=['POST'])
@jwt_required()
def add_item():
    try:
        if not check_user_permission():
            return jsonify({'message': 'Unauthorized'}), 403
    except Exception as e:
        return jsonify({'message': str(e)}), 403

    try:
        data = ItemDataModel(**request.form)
    except ValidationError as e:
        return jsonify({'message': 'Invalid input', 'errors': e.errors()}), 400

    name = data.name
    description = data.description
    features = data.features
    price = data.price
    images: List[FileStorage] = request.files.getlist('images')
    images_url: List[str] = []

    for image in images:
        if not allowed_file(image.filename):
            return jsonify({'message': 'File type not allowed'}), 400
        image_url = upload_image(image)
        images_url.append(image_url)

    try:
        item = create_item(name, description, features, price, images_url)
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
    return jsonify({'item': item.to_detail_dict()}), 201


@item_bp.route('', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify({'items': [item.to_dict() for item in items]}), 200


@item_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id: int):
    item: Optional[Item] = Item.query.get(item_id)
    if not item:
        return jsonify({'message': 'Item not found'}), 404
    return jsonify({'item': item.to_detail_dict()}), 200


@item_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_item(item_id: int):
    try:
        if not check_user_permission():
            return jsonify({'message': 'Unauthorized'}), 403
    except Exception as e:
        return jsonify({'message': str(e)}), 403

    item: Optional[Item] = Item.query.get(item_id)
    if not item:
        return jsonify({'message': 'Item not found'}), 404

    try:
        delete_item(item)
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
    return jsonify({'message': 'Item deleted'}), 200


@item_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def edit_item(item_id: int):
    try:
        if not check_user_permission():
            return jsonify({'message': 'Unauthorized'}), 403
    except Exception as e:
        return jsonify({'message': str(e)}), 403

    try:
        data = ItemDataModel(**request.form)
    except ValidationError as e:
        return jsonify({'message': 'Invalid input', 'errors': e.errors()}), 400

    name = data.name
    description = data.description
    features = data.features
    price = data.price
    images: List[FileStorage] = request.files.getlist('images')
    images_url: List[str] = []

    for image in images:
        if not allowed_file(image.filename):
            return jsonify({'message': 'File type not allowed'}), 400
        image_url = upload_image(image)
        images_url.append(image_url)
        print(images_url)

    try:
        item: Optional[Item] = Item.query.get(item_id)
        item = update_item(item, name, description, features, price, images_url)
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

    return jsonify({'item': item.to_detail_dict()}), 200
