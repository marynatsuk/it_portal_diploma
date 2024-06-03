from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_url_path='/website/templates')
    app.config['SECRET_KEY'] = 'skvjnalskdjvn alksdjvnasdlkjvn '
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://y5a0wio6vcbnulj3:cubobue7ca7ygzc1@i5x1cqhq5xbqtv00.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/a8qw1jnn66b9rf2v'
    db.init_app(app)

    from .models import Worker, Role, Department
    from .admin_views import admin_views
    from .auth import auth
    from .manager_views import manager_views
    from .user_views import user_views

    app.register_blueprint(admin_views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(manager_views, url_prefix='/manager')
    app.register_blueprint(user_views, url_prefix='/user')

    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Worker.query.get(int(id))

    return app


