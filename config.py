import os
from pathlib import Path
basedir = str(Path(__file__).parent.absolute())

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very secure password'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'oauth.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
