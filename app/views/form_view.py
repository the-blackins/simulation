import json
import traceback
from sqlalchemy.orm.collections import InstrumentedList
from datetime import datetime

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)

from app.services.simulation_service import SimulationEngine
from app.services.simulation_config import create_simulations

form_bp = Blueprint('form', __name__)
home_bp = Blueprint('home', __name__)

@home_bp.route('/', methods=['GET'])    
def landing_page():
    return render_template('index.html')

@home_bp.route('/simulation-setup', methods=['GET'])
def simulation_setup():
    return render_template('form.html')

@form_bp.route('/api/submit-simulation', methods=['POST'])
def submit_simulation_form():
    try:         
        # Parse and validate JSON data
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        required_fields = ['numStudents', 'numSimulations', 'finalLevel', 'universities']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        from database.seeds import seed_data  # Import directly since it's used

        # Seed data with universities and student count
        seed_data(data['universities'], data['numStudents'])

        # Log simulation details
        print(f"Simulation created with: students={data['numStudents']}, "
              f"simulations={data['numSimulations']}, level={data['finalLevel']}, universities={data['universities']}")
        
        return jsonify({
            'status': 'success',
            'message': 'Simulation created successfully',
            'redirect_url': url_for('simulate.simulation_page')
        }), 200

    
    except Exception as e:
        print("Server error:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

simulate_bp = Blueprint('simulate', __name__)
simulation_engine = SimulationEngine() 

@simulate_bp.route('/simulate')
def simulation_page():
    import app
    try:
        return render_template('simulation.html')
    except Exception as e:
        # app.logger.error(f"Error rendering simulation page: {str(e)}")
        return str(e), 500

@simulate_bp.route('/api/run_step', methods=['POST'])
def run_simulation_step():
    from app import db
    from app.models import (ExternalFactors, InstitutionalFactors, Student,University,
                            TestResult, Simulation)
    """run the simualtion based on university base"""
    try:
        # Query all students
        students = Student.query.all()
        universities = University.query.all()
       
        for university in universities:  # Iterate through University objects
            simulation = Simulation(
                university_id=university.id,  # Use the university's ID
                start_time=datetime.now(),
                status="Pending"
            )
            
            db.session.add(simulation)
            db.session.commit()
            
            institutional_factors = InstitutionalFactors(
                simulation_id=simulation.id
            )
            db.session.add(institutional_factors)
            db.session.commit()
        results = []
        for student in students:
            try: 
                university = next((u for u in universities if u.id == student.university_id), None)
                if not university:
                    print(f"No matching university found for student {student.id}")
                    continue

                def process_factors(factors, factor_type, identifier):
                    """Process factors if they are an InstrumentedList."""
                    if isinstance(factors, InstrumentedList):
                        if factors:
                            for factor in factors:
                                simulation_engine.update_factors(factor)
                        else:
                            print(f"No {factor_type} found for {identifier}")
                    else:
                        # Handle single object case
                        simulation_engine.update_factors(factors)

                # Processing each type of factors
                university_factors = university.institutional_factors
                process_factors(university_factors, "institutional factors", f"university {university.id}")

                external_factors = student.external_factors
                process_factors(external_factors, "external factors", f"student {student.id}")

                internal_factors = student.internal_factors
                process_factors(internal_factors, "internal factors", f"student {student.id}")

                # if not (student.external_factors and student.internal_factors and student.university_id):
                #     print(f"Missing required data for student {student.id}")
                #     continue
                score = simulation_engine.calculate_performance(student)

                # Create and save test result
                test_result = TestResult(student_id=student.id, score=score)
                db.session.add(test_result)

                # Add result to the response
                results.append({
                    'student_id': student.id,
                    'score': score,
                    'university': student.university_id
                })
            except Exception as e:
                print(f"Error processing student {student.id}: {str(e)}")  # Debugging
                continue

        # Commit changes
        db.session.commit()

        # Return results
        return jsonify({'status': 'success', 'results': results})

    except Exception as e:
        db.session.rollback()
        print(f"Simulation step error: {str(e)}")  # Debugging
        return jsonify({'status': 'error', 'message': str(e)}), 500


# # Add an error handler for 404
# @simulate_bp.errorhandler(404)
# def not_found_error(error):
#     return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404# Add this temporary route to verify your database has data

# @simulate_bp.route('/check_data')
# def check_data():
#     from app.models import Student
#     students = Student.query.all()
#     return jsonify({
#         'student_count': len(students),
#         'students': [{
#             'id': s.id,
#             'has_external': bool(s.external_factors),
#             'has_internal': bool(s.internal_factors),
#             'has_university': bool(s.university_id)
#         } for s in students]
#     })

                          