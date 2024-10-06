from flask import Flask
from .extensions import db, migrate
from .config import config


def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config[config_name])
    app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)
    migrate.init_app(app, db)

    from .views.user_views import user_bp
    from .views.face_views import face_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(face_bp, url_prefix='/api/face')
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
