from app import create_app, socketio
from flask_socketio import SocketIO

# Create the Flask application
app = create_app()


if __name__ == "__main__":
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    socketio.run(app=app, host="127.0.0.1", port=5000, debug=True)
