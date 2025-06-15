import logging
from log.logger import logger

from flask import Flask
# from .views.seeding_view import seeding_blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from .config import get_config
# from database.setup import initialize_db

db = SQLAlchemy()
cors = CORS()
socketio = SocketIO(cors_allowed_origins="http://localhost:5000")
from .models import * 


def create_app():
    # Create the Flask app instance
    app = Flask(__name__, instance_relative_config=True)
    socketio.init_app(app)

    # Load configuration from config.py
    app.config.from_object(get_config())

    # Initialize database and migrations
    from flask_migrate import Migrate
    migrate = Migrate()

    db.init_app(app)#type: ignore
    # Initialize the database with the app
    migrate.init_app(app, db) #type: ignore

    
    cors.init_app(app)
    

    from .views.views import form_bp, home_bp, simulate_bp
    # Example usage
    configure_logger(app)
    # Register blueprints (if any)
    # Register the blueprint
    app.register_blueprint(home_bp)
    app.register_blueprint(form_bp, url_prefix='/form') 
    app.register_blueprint(simulate_bp, url_prefix='/simulation')

    # app.register_blueprint(seeding_blueprint)
    # Handle errors (404 example)
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    return app



def configure_logger(app):
    # Set up logging
    
    app.logger = logging.getLogger(__name__)