from app import create_app

# Create the Flask application
app = create_app()



if __name__ == "__main__":
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(debug=True)
