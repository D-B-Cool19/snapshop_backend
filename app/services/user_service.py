from werkzeug.security import generate_password_hash
from ..models.user import User
from ..extensions import db


def create_user(username, email, password, gender, age=None, face_img_url=None, embedding=None, role=0):
    try:
        password_hash = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            gender=gender,
            age=age,
            face_img_url=face_img_url,
            role=role,
            embedding=embedding
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user
    except Exception as e:
        db.session.rollback()
        raise e


def deduct_user_count(user: User, count: int):
    try:
        if user.count < count:
            raise ValueError(f'User {user.username} does not have enough credits')
        user.count -= count
        db.session.commit()

        return user
    except Exception as e:
        db.session.rollback()
        raise e
