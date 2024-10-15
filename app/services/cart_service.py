from app import db
from app.models.cart_item import CartItem


def create_cart_item(user_id, item_id, quantity=1, checked=True):
    try:
        new_cart_item = CartItem(
            user_id=user_id,
            item_id=item_id,
            quantity=quantity,
            checked=checked
        )
        db.session.add(new_cart_item)
        db.session.commit()

        return new_cart_item
    except Exception as e:
        db.session.rollback()
        raise e


def update_cart_item(cart_item: CartItem, quantity=None, checked=None):
    try:
        if quantity:
            cart_item.quantity = quantity
        if checked is not None:
            cart_item.checked = checked

        db.session.commit()

        return cart_item
    except Exception as e:
        db.session.rollback()
        raise e


def delete_cart_item(cart_item: CartItem):
    try:
        db.session.delete(cart_item)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
