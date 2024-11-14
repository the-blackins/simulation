from flask import Flask
from .config import get_config
from database.setup import initialize_db
from .views.form_view import form_bp
from flask_cors import CORS

cors = CORS()


def create_app():
    # Create the Flask app instance
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration from config.py
    app.config.from_object(get_config())

    # Initialize database and migrations
    initialize_db(app)
    cors.init_app(app)
    
    # Register blueprints (if any)
    # Register the blueprint
    app.register_blueprint(form_bp)

    # Handle errors (404 example)
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    return app
