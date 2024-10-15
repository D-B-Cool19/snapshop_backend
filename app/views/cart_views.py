import math
from typing import Optional, List
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..models.cart_item import CartItem
from ..models.user import User
from ..models.item import Item
from ..services.cart_service import create_cart_item, update_cart_item, delete_cart_item
from ..services.user_service import deduct_user_count

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/item/<int:item_id>', methods=['POST'])
@jwt_required()
def add_cart(item_id: int):
    try:
        user_id = get_jwt_identity()['id']
        quantity = int(request.json.get('quantity', 1))

        if quantity < 0 or quantity > 1000:
            return jsonify({'message': 'Invalid quantity'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        item = Item.query.get(item_id)
        if not item:
            return jsonify({'message': 'Item not found'}), 404

        cart_item: Optional[CartItem] = CartItem.query.filter_by(user_id=user_id, item_id=item_id).first()
        if cart_item:
            cart_item = update_cart_item(cart_item, quantity=cart_item.quantity + quantity)
        else:
            cart_item = create_cart_item(user_id, item_id, quantity)
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    return jsonify(cart_item.to_dict()), 200


@cart_bp.route('/<int:cart_item_id>', methods=['PUT'])
@jwt_required()
def update_cart(cart_item_id: int):
    try:
        quantity = int(request.json.get('quantity', 1))
        checked = request.json.get('checked', True)

        if quantity < 0 or quantity > 1000:
            return jsonify({'message': 'Invalid quantity'}), 400

        if checked is None or not isinstance(checked, bool):
            return jsonify({'message': 'Invalid checked'}), 400

        cart_item = CartItem.query.get(cart_item_id)
        if not cart_item:
            return jsonify({'message': 'Cart item not found'}), 404

        cart_item = update_cart_item(cart_item, quantity=quantity, checked=checked)
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    return jsonify({'item': cart_item.to_dict()}), 200


@cart_bp.route('/<int:cart_item_id>', methods=['DELETE'])
@jwt_required()
def delete_cart(cart_item_id: int):
    try:
        cart_item = CartItem.query.get(cart_item_id)
        if not cart_item:
            return jsonify({'message': 'Cart item not found'}), 404
        delete_cart_item(cart_item)
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    return jsonify({'message': 'Cart item deleted'}), 200


@cart_bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    try:
        user_id = get_jwt_identity()['id']
        cart_items: List[CartItem] = CartItem.query.filter_by(user_id=user_id).all()
        return jsonify({'cartItems': [cart_item.to_dict() for cart_item in cart_items]}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cart_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    try:
        user_id = get_jwt_identity()['id']
        count = int(request.json.get('credits', 0))
        discount = count / 10
        user: Optional[User] = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        if count < 0:
            return jsonify({'message': 'Invalid credits'}), 400
        if user.count < count:
            return jsonify({'message': 'Not enough credits'}), 400

        cart_items: List[CartItem] = CartItem.query.filter_by(user_id=user_id, checked=True).all()
        if not cart_items:
            return jsonify({'message': 'No items in cart'}), 400

        total_price = sum([cart_item.item.price * cart_item.quantity for cart_item in cart_items])
        if total_price < discount:
            return jsonify({'message': 'Use too much credits'}), 400

        price = total_price - discount
        refund = math.floor(price / 5)
        user = deduct_user_count(user, count - refund)

        for cart_item in cart_items:
            delete_cart_item(cart_item)
        return jsonify({'message': 'Checkout successful',
                        'user': user.to_dict(),
                        'originalPrice': total_price,
                        'discount': discount,
                        'refund': refund,
                        'totalPrice': total_price - discount}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
