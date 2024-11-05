import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

def get_config():
    """Returns a dictionary of configuration settings."""
    return {
        'SECRET_KEY': os.getenv("SECRET_KEY"),
        'SQLALCHEMY_DATABASE_URI': os.getenv("DATABASE_URI", "sqlite:///../instance/database.db"),  # Updated to point to the instance folder
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
