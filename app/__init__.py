# import os
# from flask import Flask
# from dotenv import load_dotenv
# from .config import get_config
# from database.setup import initialize_db

# def create_app():
#     # Create and configure the app
#     app = Flask(__name__, instance_relative_config=True)  # Use instance_relative_config for instance folder support

#     # Load configuration from .env
#     load_dotenv()
#     app.config.update(get_config())

#     initialize_db(app)

#     # Register blueprints
#     # Example: app.register_blueprint(your_blueprint)

#     # Handle errors (404 example)

#     return app


import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the database and migration
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Create and configure the Flask app
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from environment variables
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI", "sqlite:///database.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database and migration extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints (if you have any)
    # Example: app.register_blueprint(your_blueprint)

    # Handle errors (404 example)
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    return app

