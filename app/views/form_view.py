from flask import Flask, render_template, request, jsonify, Blueprint, current_app
from app.models import Simulation
from datetime import datetime
from database.setup import db
import traceback  # Add this import

form_bp = Blueprint('main', __name__)

@form_bp.route('/', methods=['GET'])
def show_form():
    return render_template('index.html')

@form_bp.route('/api/submit-simulation', methods=['POST'])
def submit_simulation():
    try:
        # Print the raw request data for debugging
        print("Received data:", request.get_data())
        print("Content Type:", request.headers.get('Content-Type'))
        
        # Get the JSON data from the form submission
        data = request.get_json()
        print("Parsed JSON data:", data)  # Debug print
        
        # Validate required fields
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
            
        required_fields = ['numStudents', 'numSimulations', 'finalLevel']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400

        # Print the values before creating the object
        print(f"Creating simulation with: students={data['numStudents']}, "
              f"simulations={data['numSimulations']}, level={data['finalLevel']}")

        new_simulation = Simulation(
            num_students=int(data['numStudents']),  # Ensure integers
            num_simulations=int(data['numSimulations']),
            final_level=int(data['finalLevel']),
            status='pending'  # Remove created_at as it's handled by default
        )

        try:
            db.session.add(new_simulation)
            db.session.commit()
            print(f"Successfully created simulation with ID: {new_simulation.id}")

            return jsonify({
                'status': 'success',
                'message': 'Simulation configuration saved successfully',
                'data': {
                    'id': new_simulation.id,
                    'num_students': new_simulation.num_students,
                    'num_simulations': new_simulation.num_simulations,
                    'final_level': new_simulation.final_level,
                    'status': new_simulation.status,
                    'created_at': new_simulation.created_at.isoformat()
                }
            }), 201
            
        except Exception as db_error:
            db.session.rollback()
            print("Database error:", str(db_error))
            print("Traceback:", traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': f'Database error: {str(db_error)}'
            }), 500
            
    except Exception as e:
        print("Server error:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500