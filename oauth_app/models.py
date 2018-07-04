from flask_login import UserMixin, current_user
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from oauth_app import db, login_manager, blueprint

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

# setup SQLAlchemy backend
blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
