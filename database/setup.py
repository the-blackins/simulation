# database/setup.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.ext.declarative import declarative_base

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

Base = declarative_base()

def initialize_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
