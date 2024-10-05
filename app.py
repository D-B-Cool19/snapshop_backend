from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sqlalchemy import text  # 导入 text 模块
import config
from exts import db
from flask_migrate import Migrate
import secrets

app = Flask(__name__)

app.config.from_object(config)
app.config['SECRET_KEY'] = secrets.token_hex(16)
db.init_app(app)


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    # 添加一个列来存储产品 URL
    url = db.Column(db.String(255), nullable=True)  # 255 或者其他长度根据您的需求来定


class Orders(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)


class OrderItems(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)


class Points(db.Model):
    __tablename__ = "points"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)


with app.app_context():
    # 手动创建新表
    db.create_all()

with app.app_context():
    with db.engine.connect() as conn:
        rs = conn.execute(text("SELECT 1"))
        print(rs.fetchone())


@app.route('/')
def hello_world():
    username = session.get('username')  # 获取当前用户的用户名
    return render_template("index.html", username=username)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 检查用户名是否已经存在
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            return '用户名已存在，请选择其他用户名'

        # 创建新用户
        new_user = Users(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('register_success.html', username=username)

    background_image_url = url_for('static', filename='image/fig2.png')
    return render_template('register.html', background_image_url=background_image_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 查询数据库中是否存在匹配的用户
        user = Users.query.filter_by(username=username, password=password).first()

        if user:
            # 登录成功，设置用户会话
            # 登录成功，设置用户会话
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('hello_world'))
        else:
            return '用户名或密码错误，请重新输入！'

    return render_template('login.html')


@app.route('/all_goods')
def all_goods():
    return render_template('all_goods.html')


@app.route('/higtory')
def history():
    return render_template('history.html')


@app.route('/pay_suc')
def pay_suc():
    return render_template('pay_suc.html')


@app.route('/success')
def success():
    return redirect(url_for('index'))


@app.route('/faceID')
def faceID():
    # 处理人脸识别的逻辑
    return render_template('faceID.html')


@app.route('/score_suc')
def score_suc():
    return render_template('score_suc.html')


@app.route('/forgetpassword')
def forgetpassword():
    # 处理忘记密码逻辑
    return render_template('forgetpassword.html')


@app.route('/reset')
def reset_password():
    # 处理重置密码逻辑
    return render_template('reset.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/score')
def score():
    return render_template('score.html')


@app.route('/user/add')
def add_user():
    try:
        user = Users(username="张三", password='11111111')
        db.session.add(user)
        db.session.commit()
        return "用户创建成功"
    except Exception as e:
        return f"发生错误: {e}"


@app.route('/profile')
def profile():
    username = session.get('username')
    return render_template('profile.html', username=username)


@app.route("/user/query")
def query_user():
    try:
        users = Users.query.filter_by(username="张三").all()
        if not users:  # 如果列表为空
            return "数据查找失败"

        # 打印查询结果
        for user in users:
            print(f"{user.id}:{user.username}-{user.password}")

        return "数据查找成功"

    except Exception as e:
        return f"发生错误: {e}"


@app.route("/user/update")
def update_user():
    user = Users.query.filter_by(username="张三").first()
    user.password = "2222222"
    db.session.commit()
    return "数据修改成功"


@app.route('/user/delete')
def delete_user():
    try:
        users = Users.query.filter_by(username="张三").all()

        if not users:  # 如果用户列表为空
            return "数据删除失败，未找到匹配的用户"

        for user in users:
            db.session.delete(user)

        db.session.commit()  # 提交事务

        return "数据删除成功"

    except Exception as e:
        db.session.rollback()  # 发生异常时回滚事务
        return f"发生错误: {e}"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
