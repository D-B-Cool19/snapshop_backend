from typing import Optional, List

from ..extensions import db


class CartItem(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id: int = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity: int = db.Column(db.Integer, nullable=False, default=1)
    checked: bool = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', back_populates='cart_items')
    item = db.relationship('Item', back_populates='cart_items')

    def to_dict(self):
        return {
            "id": self.id,
            "item": self.item.to_dict(),
            "quantity": self.quantity,
            "checked": self.checked
        }
