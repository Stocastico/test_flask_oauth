import sys
from oauth_app import app, db
from oauth_app.models import User, OAuth

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'OAuth': OAuth}

if __name__ == "__main__":
    if "--setup" in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print("Database tables created")
    else:
        app.run(debug=True)
