from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import timedelta
from .extensions import db, migrate
from .config import config
from flask_cors import CORS


def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config[config_name])
    app.config.from_pyfile('config.py', silent=True)
    app.config['JWT_SECRET_KEY'] = 'this_is_my_jwt_secret_key_cool19'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

    JWTManager(app)
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from .views.user_views import user_bp
    from .views.face_views import face_bp
    from .views.item_views import item_bp
    from .views.cart_views import cart_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(face_bp, url_prefix='/api/face')
    app.register_blueprint(item_bp, url_prefix='/api/item')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')

    return app
