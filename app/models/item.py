from typing import Optional, List

from ..extensions import db


class Item(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(80), unique=True, nullable=False)
    description: str = db.Column(db.String(1200), nullable=False)
    features: str = db.Column(db.String(1200), nullable=False)
    price: float = db.Column(db.Float, nullable=False)
    images: List[str] = db.Column(db.PickleType, nullable=False)
    rate: float = db.Column(db.Float, default=0)
    reviews: int = db.Column(db.Integer, default=0)
    cart_items = db.relationship('CartItem', back_populates='item')

    def to_detail_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "features": self.features,
            "price": self.price,
            "images": self.images,
            "rate": self.rate,
            "reviews": self.reviews
        }

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "rate": self.rate,
            "image": self.images[0] if self.images else None,
            "description": self.description
        }
