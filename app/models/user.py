from typing import Optional

from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(255), nullable=False)
    gender: str = db.Column(db.String(10))
    age: Optional[int] = db.Column(db.Integer)
    face_img_url: Optional[str] = db.Column(db.String(255))
    role: int = db.Column(db.Integer)
    count: int = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "gender": self.gender,
            "age": self.age,
            "faceImgUrl": self.face_img_url,
            "role": self.role,
            "count": self.count
        }
