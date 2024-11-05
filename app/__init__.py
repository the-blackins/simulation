

from flask import Flask
from .config import get_config
from database.setup import db, migrate, initialize_db

def create_app():
    # Create the Flask app instance
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from config.py
    app.config.from_object(get_config())

    # Initialize database and migrations
    initialize_db(app)

    # Register blueprints (if any)
    # Example: app.register_blueprint(your_blueprint)

    # Handle errors (404 example)
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    return app
