from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_dance.contrib.github import make_github_blueprint, github

app = Flask(__name__)
app.config.from_object(Config)

blueprint = make_github_blueprint(
    client_id="1c149085aa7e212c802e",
    client_secret="74ef50f8bc1f229b3732104ab6d5772395566315",
)
app.register_blueprint(blueprint, url_prefix="/login")

# setup database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# setup login manager
login_manager = LoginManager(app)
login_manager.login_view = 'github.login'

# hook up extensions to app
db.init_app(app)
login_manager.init_app(app)

from oauth_app import routes, models
