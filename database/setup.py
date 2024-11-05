# database/setup.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def initialize_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
