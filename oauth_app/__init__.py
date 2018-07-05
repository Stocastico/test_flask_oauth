from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter

app = Flask(__name__)
app.config.from_object(Config)

bp_github = make_github_blueprint(
    client_id="1c149085aa7e212c802e",
    client_secret="74ef50f8bc1f229b3732104ab6d5772395566315",
)
app.register_blueprint(bp_github, url_prefix="/github_login")

bp_google = make_google_blueprint(
    client_id="309187282036-qejd4n4j625pq1dnljll68smk6gqlsd8.apps.googleusercontent.com",
    client_secret="IocbQkBvurElM63vBHTpqOKi",
    scope=["profile", "email"]
)
app.register_blueprint(bp_google, url_prefix="/google_login")

bp_twitter = make_twitter_blueprint(
    api_key="dnhKngpFnwe64pY6NdlxePRUO",
    api_secret="nk9Q4lj7yubGyHypqCCXhfvspj0tGDyGMD7oEzf4zvpU8ZB165",
)
app.register_blueprint(bp_twitter, url_prefix="/twitter_login")


# setup database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# setup login manager
login_manager = LoginManager(app)
login_manager.login_github_view = 'github.login'
login_manager.login_google_view = 'google.login'
login_manager.login_twitter_view = 'twitter.login'

# hook up extensions to app
db.init_app(app)
login_manager.init_app(app)

from oauth_app import routes, models
