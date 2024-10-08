from werkzeug.security import generate_password_hash
from ..models.user import User
from ..extensions import db


# 创建用户服务函数
def create_user(username, email, password, gender, age=None, face_img_url=None, role=0):
    try:
        password_hash = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            gender=gender,
            age=age,
            face_img_url=face_img_url,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user
    except Exception as e:
        db.session.rollback()
        raise e
