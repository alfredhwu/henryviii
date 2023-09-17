import os

from flask import Flask, url_for

def create_dir_if_not_exist(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'upload'),
        DELETE_AFTER_SYNC=True
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        create_dir_if_not_exist(app.instance_path)
        create_dir_if_not_exist(app.config["UPLOAD_FOLDER"])
    except OSError as e:
        app.logger.error(f"Error: {e}")
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World! from Flask'

    from . import db
    db.init_app(app)

    from .controller import auth, account, admin, article, off_account, user_category, dashboard


    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(account.bp, url_prefix='/account')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(off_account.bp, url_prefix='/off-account')
    app.register_blueprint(user_category.bp, url_prefix='/user-category')
    app.register_blueprint(article.bp)
    app.register_blueprint(dashboard.bp)

    app.add_url_rule('/', endpoint='index')

    return app
