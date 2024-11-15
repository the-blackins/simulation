import requests
from flask import Blueprint, request
from database.seeds import seed_data

seeding_blueprint = Blueprint('seeding', __name__)

@seeding_blueprint.route('/seed_data', methods=['POST'])
def seed_data():
    # Fetch data from the external API endpoint
    # response = requests.get('http://localhost:5000/api/submit-simulation')  # replace with actual URL
    # form_data = response.json()
    
    # form_universities = []
    # if 'universities' in form_data:
    #     form_universities = form_data['universities']

    # Retrieve num_students from request data or set default
    num_students = request.json.get('num_students', 100)

    # Call your seeding function here
    # seed_data(form_universities, num_students)

    return {'message': 'Database seeded successfully'}

