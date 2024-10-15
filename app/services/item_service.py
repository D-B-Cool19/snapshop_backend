from ..models.item import Item
from ..extensions import db


def create_item(name, description, features, price, images, rate=0, reviews=0):
    try:
        new_item = Item(
            name=name,
            description=description,
            features=features,
            price=price,
            images=images,
            rate=rate,
            reviews=reviews
        )
        db.session.add(new_item)
        db.session.commit()

        return new_item
    except Exception as e:
        db.session.rollback()
        raise e


def update_item(item: Item, name=None, description=None, features=None, price=None, images=None):
    try:
        if name:
            item.name = name
        if description:
            item.description = description
        if features:
            item.features = features
        if price:
            item.price = price
        if images:
            item.images = images

        db.session.commit()

        return item
    except Exception as e:
        db.session.rollback()
        raise e


def delete_item(item: Item):
    try:
        db.session.delete(item)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
