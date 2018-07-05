from flask import redirect, url_for, flash, render_template
from sqlalchemy.orm.exc import NoResultFound
from flask_login import login_user, login_required, logout_user, current_user
from flask_dance.consumer import oauth_authorized, oauth_error
import pprint
from oauth_app import app, db, bp_github, bp_google, bp_twitter
from oauth_app.models import OAuth, User


# create/login local user on successful OAuth login with github or google
@oauth_authorized.connect_via(bp_github)
@oauth_authorized.connect_via(bp_google)
@oauth_authorized.connect_via(bp_twitter)
def logged_in(blueprint, token):
    if not token:
        flash("Failed to log in.", category="error")
        return False

    session = blueprint.session
    print('SESSION IS: {}'.format(session))

    provider = None  # could be Github, Google or Twitter at the moment

    # try Github
    resp = session.get("/user")
    print('1 -- RESPONSE IS {}'.format(resp))
    provider = "Github"
    if resp.status_code == 404:  # page not found
        # try Google
        resp = session.get("/oauth2/v2/userinfo")
        print('2 -- RESPONSE IS {}'.format(resp))
        provider = "Google"
        if resp.status_code == 404:  # page not found
            # try Twitter
            payload = {'include_email': 'true'}
            resp = session.get("account/verify_credentials.json",
                                params=payload)
            print('3 -- RESPONSE IS {}'.format(resp))
            provider = "Twitter"

    if not resp.ok:
        print('4 -- RESPONSE IS {}'.format(resp))
        msg = "Failed to fetch user info."
        flash(msg, category="error")
        provider = None
        return False

    info = resp.json()
    pprint.pprint(info)

    if provider == "Github" or provider == "Google":
        user_id = str(info["id"])
    elif provider == "Twitter":
        user_id = str(info['id_str'])
    else:
        raise ValueError("Unknown provider")

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in.")

    else:
        # Create a new local user account for this user
        if provider == "Github":
            name = info['login']
        elif provider == "Google" or provider == "Twitter":
            name = info['name']
        else:
            raise ValueError("Unknown provider")

        user = User(
            # Remember that `email` can be None, if the user declines
            # to publish their email address on GitHub!
            email=info["email"],
            name=name
        )
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in.")

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


# # create/login local user on successful OAuth login with github
# @oauth_authorized.connect_via(bp_github)
# def github_logged_in(blueprint, token):
#     if not token:
#         flash("Failed to log in with GitHub.", category="error")
#         return False

#     resp = blueprint.session.get("/user")
#     if not resp.ok:
#         msg = "Failed to fetch user info from GitHub."
#         flash(msg, category="error")
#         return False

#     github_info = resp.json()
#     print(github_info)
#     github_user_id = str(github_info["id"])

#     # Find this OAuth token in the database, or create it
#     query = OAuth.query.filter_by(
#         provider=blueprint.name,
#         provider_user_id=github_user_id,
#     )
#     try:
#         oauth = query.one()
#     except NoResultFound:
#         oauth = OAuth(
#             provider=blueprint.name,
#             provider_user_id=github_user_id,
#             token=token,
#         )

#     if oauth.user:
#         login_user(oauth.user)
#         flash("Successfully signed in with GitHub.")

#     else:
#         # Create a new local user account for this user
#         user = User(
#             # Remember that `email` can be None, if the user declines
#             # to publish their email address on GitHub!
#             email=github_info["email"],
#             name=github_info["login"]
#         )
#         # Associate the new local user account with the OAuth token
#         oauth.user = user
#         # Save and commit our database models
#         db.session.add_all([user, oauth])
#         db.session.commit()
#         # Log in the new local user account
#         login_user(user)
#         flash("Successfully signed in with GitHub.")

#     # Disable Flask-Dance's default behavior for saving the OAuth token
#     return False

# # create/login local user on successful OAuth login with google
# @oauth_authorized.connect_via(bp_google)
# def google_logged_in(blueprint, token):
#     if not token:
#         flash("Failed to log in with Google.", category="error")
#         return False

#     resp = blueprint.session.get("/oauth2/v2/userinfo")
#     if not resp.ok:
#         msg = "Failed to fetch user info from Google."
#         flash(msg, category="error")
#         return False

#     google_info = resp.json()
#     print(google_info)
#     google_user_id = str(google_info["id"])

#     # Find this OAuth token in the database, or create it
#     query = OAuth.query.filter_by(
#         provider=blueprint.name,
#         provider_user_id=google_user_id,
#     )
#     try:
#         oauth = query.one()
#     except NoResultFound:
#         oauth = OAuth(
#             provider=blueprint.name,
#             provider_user_id=google_user_id,
#             token=token,
#         )

#     if oauth.user:
#         login_user(oauth.user)
#         flash("Successfully signed in with Google.")

#     else:
#         # Create a new local user account for this user
#         user = User(
#             email=google_info["email"],
#             name=google_info["name"]
#         )
#         # Associate the new local user account with the OAuth token
#         oauth.user = user
#         # Save and commit our database models
#         db.session.add_all([user, oauth])
#         db.session.commit()
#         # Log in the new local user account
#         login_user(user)
#         flash("Successfully signed in with Google.")

#     # Disable Flask-Dance's default behavior for saving the OAuth token
#     return False

# notify on OAuth provider error (github / google)
@oauth_error.connect_via(bp_github)
@oauth_error.connect_via(bp_google)
@oauth_error.connect_via(bp_twitter)
def github_error(blueprint, error, error_description=None, error_uri=None):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for("index"))

@app.route("/")
def index():
    return render_template("home.html")
