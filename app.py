# import os
# import uuid
# from typing import Optional
# from pydantic import BaseModel, ValidationError, EmailStr, Field, field_validator
# from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory
# from sqlalchemy import text  # 导入 text 模块
# from werkzeug.datastructures import FileStorage
# from werkzeug.utils import secure_filename
#
# from app import config
# from app.extensions import db
# from flask_migrate import Migrate
# import secrets
#
# from app.models.user import User
#
# app = Flask(__name__)
#
# app.config.from_object(config)
# app.config['SECRET_KEY'] = secrets.token_hex(16)
# db.init_app(app)
#
# migrate = Migrate(app, db)
#
# #
# # class Products(db.Model):
# #     __tablename__ = "products"
# #     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
# #     name = db.Column(db.String(100), nullable=False)
# #     price = db.Column(db.Float, nullable=False)
# #     # 添加一个列来存储产品 URL
# #     url = db.Column(db.String(255), nullable=True)  # 255 或者其他长度根据您的需求来定
# #
# #
# # class Orders(db.Model):
# #     __tablename__ = "orders"
# #     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
# #     user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
# #     order_date = db.Column(db.DateTime, nullable=False)
# #     total_amount = db.Column(db.Float, nullable=False)
# #
# #
# # class OrderItems(db.Model):
# #     __tablename__ = "order_items"
# #     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
# #     order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
# #     product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
# #     quantity = db.Column(db.Integer, nullable=False)
# #     price = db.Column(db.Float, nullable=False)
# #
# #
# # class Points(db.Model):
# #     __tablename__ = "points"
# #     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
# #     user_id = db.Column(db.Integer, db.ForeignKey('User.id'), unique=True, nullable=False)
# #     points = db.Column(db.Integer, nullable=False, default=0)
#
#
# with app.app_context():
#     print('create')
#     db.create_all()
#
# with app.app_context():
#     with db.engine.connect() as conn:
#         rs = conn.execute(text("SELECT 1"))
#         print(rs.fetchone())
#
# if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     os.makedirs(app.config['UPLOAD_FOLDER'])
#
#
# def allowed_file(filename):
#     allowed_extensions = {"png", "jpg", "jpeg", "gif"}
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
#
#
# @app.route('/api/user/register', methods=['POST'])
# def register():
#     class UserDataModel(BaseModel):
#         username: str = Field(..., min_length=4, max_length=20,
#                               description="Username must be between 4 and 20 characters")
#         email: EmailStr
#         password: str = Field(..., min_length=8, max_length=20,
#                               description="Password must be between 8 and 20 characters")
#         gender: str = Field(..., pattern="^(male|female|unknown)$",
#                             description="Gender must be either 'male', 'female', or 'unknown'")
#         age: Optional[int] = Field(None, ge=1, le=120, description="Age must be between 1 and 120")
#
#         @field_validator('age', mode='before')
#         def convert_age(cls, value):
#             if value is None or value == "":
#                 return None
#             if isinstance(value, str) and value.isdigit():
#                 return int(value)
#             if isinstance(value, int):
#                 return value
#             raise ValueError('Age must be a valid integer')
#
#     try:
#         data = UserDataModel(**request.form)
#     except ValidationError as e:
#         return jsonify({"message": "Invalid input", "errors": e.errors()}), 400
#
#     username = data.username
#     password = data.password
#     email = data.email
#     gender = data.gender
#     age = data.age
#     face_img: Optional[FileStorage] = request.files.get("faceImg")
#
#     try:
#         if User.query.filter_by(username=username).first() is not None:
#             return jsonify({"message": "User already exists"}), 400
#
#         if User.query.filter_by(email=email).first() is not None:
#             return jsonify({"message": "Email already exists"}), 400
#
#         face_img_url: Optional[str] = None
#         if face_img:
#             if not allowed_file(face_img.filename):
#                 return jsonify({"message": "File type not allowed"}), 400
#
#             file_ext = os.path.splitext(secure_filename(face_img.filename))[1]
#             filename = f"{uuid.uuid4().hex}{file_ext}"
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#
#             try:
#                 face_img.save(file_path)
#                 face_img_url = url_for('uploaded_file', filename=filename, _external=True)
#             except Exception as e:
#                 return jsonify({"message": f"Failed to save file: {str(e)}"}), 500
#
#         new_user = User(
#             username=username,
#             email=email,
#             gender=gender,
#             age=age,
#             face_img_url=face_img_url,
#             role=0
#         )
#         new_user.set_password(password)
#
#         db.session.add(new_user)
#         db.session.commit()
#
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"message": f"An error occurred: {str(e)}"}), 500
#
#     return jsonify({"message": "User registered successfully"}), 201
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         # 查询数据库中是否存在匹配的用户
#         user = User.query.filter_by(username=username, password=password).first()
#
#         if user:
#             # 登录成功，设置用户会话
#             # 登录成功，设置用户会话
#             session['logged_in'] = True
#             session['username'] = username
#             return redirect(url_for('hello_world'))
#         else:
#             return '用户名或密码错误，请重新输入！'
#
#     return render_template('login.html')
#
#
# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     # 从 uploads 目录发送文件
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#
#
# @app.route('/all_goods')
# def all_goods():
#     return render_template('all_goods.html')
#
#
# @app.route('/higtory')
# def history():
#     return render_template('history.html')
#
#
# @app.route('/pay_suc')
# def pay_suc():
#     return render_template('pay_suc.html')
#
#
# @app.route('/success')
# def success():
#     return redirect(url_for('index'))
#
#
# @app.route('/faceID')
# def faceID():
#     # 处理人脸识别的逻辑
#     return render_template('faceID.html')
#
#
# @app.route('/score_suc')
# def score_suc():
#     return render_template('score_suc.html')
#
#
# @app.route('/forgetpassword')
# def forgetpassword():
#     # 处理忘记密码逻辑
#     return render_template('forgetpassword.html')
#
#
# @app.route('/reset')
# def reset_password():
#     # 处理重置密码逻辑
#     return render_template('reset.html')
#
#
# @app.route('/cart')
# def cart():
#     return render_template('cart.html')
#
#
# @app.route('/score')
# def score():
#     return render_template('score.html')
#
#
# @app.route('/user/add')
# def add_user():
#     try:
#         user = User(username="张三", password='11111111')
#         db.session.add(user)
#         db.session.commit()
#         return "用户创建成功"
#     except Exception as e:
#         return f"发生错误: {e}"
#
#
# @app.route('/profile')
# def profile():
#     username = session.get('username')
#     return render_template('profile.html', username=username)
#
#
# @app.route("/user/query")
# def query_user():
#     try:
#         User = User.query.filter_by(username="张三").all()
#         if not User:  # 如果列表为空
#             return "数据查找失败"
#
#         # 打印查询结果
#         for user in User:
#             print(f"{user.id}:{user.username}-{user.password}")
#
#         return "数据查找成功"
#
#     except Exception as e:
#         return f"发生错误: {e}"
#
#
# @app.route("/user/update")
# def update_user():
#     user = User.query.filter_by(username="张三").first()
#     user.password = "2222222"
#     db.session.commit()
#     return "数据修改成功"
#
#
# @app.route('/user/delete')
# def delete_user():
#     try:
#         User = User.query.filter_by(username="张三").all()
#
#         if not User:  # 如果用户列表为空
#             return "数据删除失败，未找到匹配的用户"
#
#         for user in User:
#             db.session.delete(user)
#
#         db.session.commit()  # 提交事务
#
#         return "数据删除成功"
#
#     except Exception as e:
#         db.session.rollback()  # 发生异常时回滚事务
#         return f"发生错误: {e}"
#
#
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5001)
