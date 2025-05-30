import json

import traceback
from sqlalchemy.orm import Session
from datetime import datetime

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)

from app.services.simulation_service import SimulationService
from app.services import  loader, memory_state_population

form_bp = Blueprint('form', __name__)
home_bp = Blueprint('home', __name__)
simulate_bp = Blueprint('simulate', __name__)
# simulate_bp = Blueprint('chart_instance', __name__)


@home_bp.route('/', methods=['GET'])    
def landing_page():
    return render_template('index.html')

@home_bp.route('/simulation-setup', methods=['GET'])
def simulation_setup():
    return render_template('form.html')

@form_bp.route('/api/submit-simulation', methods=['POST'])
def submit_simulation_form():
    try:         
        from database_population.seeds import seed_data  # Import directly since it's used
        # Parse and validate JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        required_fields = ['numStudents', 'numSimulations', 'finalLevel', 'universities']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        

        # Seed data with universities and student count
        seed_data(data['universities'], data['numStudents'])

        load_memory()
        # Log simulation details
        print(f"Simulation created with: students={data['numStudents']}, "
              f"simulations={data['numSimulations']}, level={data['finalLevel']}, universities={data['universities']}")
        return jsonify({
            'status': 'success',
            'message': 'Simulation created successfully',
            'redirect_url': url_for('simulate.simulation_page',  _external=True)
        }), 200 
    
        
    except Exception as e:
        print("Server error:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


@simulate_bp.route('/load-memory')
def load_memory():
    try:       
        global simulation_data
        
        # Load initial data from the database
        from app.services import  initialize_memory

        simulation_data = initialize_memory()
        print("Simulation data initialized successfully.")

        return 'Memory loaded successfully', 200
              
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f'Error: {str(e)}', 500



@simulate_bp.route('/api/simulate')
def simulation_page():
    try:       
        
        print("route ohk ")
        
        return render_template('simulation.html'), 200
              
    except Exception as e:
        # app.logger.error(f"Error rendering simulation page: {str(e)}")
        return str(e), 500
   

                  
@simulate_bp.route('/api/chart_render')
def load_chart_instance():
    simulation_service = SimulationService()
    try:
         
        charts = simulation_service.chart_instance()
        return jsonify({"data": charts})
     
    except Exception as e:
        return str(e)


@simulate_bp.route('/api/run_step', methods=['POST'])
def run_simulation_step():
    """run the simualtion based on university base(simulation)"""
    session = Session()

    try:
        from app.services import run_simulation
        run_simulation(simulation_data)
        # Here you would typically run the simulation step
        

        


        # print("Running simulation step...")
        # run_simulation()
        # print("Simulation step completed successfully.")
        # return jsonify({'status': 'success', 'message': 'Simulation step completed successfully.'}), 200
        return jsonify({'status': 'success', 'message': 'Simulation step completed successfully.'}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify(f'error {str(e)}'), 500
    # try:
        # Query all students
        # students = Student.query.all()
        # universities = University.query.all()

       
        # # print(students)
        # results = []
        # print(chart_instance())
        # for student in students:
        #     university = next((u for u in universities if u.id == student.university_id), None)
        #     if not university:
        #         print(f"No matching university found for student {student.id}")
        #         continue

        #     def process_factors(factors, factor_type, identifier):
        #         """Process factors if they are an InstrumentedList."""
        #         if isinstance(factors, InstrumentedList):
        #             if factors:
        #                 for factor in factors:
        #                     simulation_engine.update_factors(factor)
        #             else:
        #                 print(f"No {factor_type} found for {identifier}")
        #         else:
        #             # Handle single object case
        #             simulation_engine.update_factors(factors)

        #     # Processing each type of factors
        #     university_factors = university.institutional_factors
        #     process_factors(university_factors, "institutional factors", f"university {university.id}")

        #     external_factors = student.external_factors
        #     process_factors(external_factors, "external factors", f"student {student.id}")

        #     internal_factors = student.internal_factors
        #     process_factors(internal_factors, "internal factors", f"student {student.id}")
 
        #     # if not (student.external_factors and student.internal_factors and student.university_id):
        #     #     print(f"Missing required data for student {student.id}")
        #     #     continue
        #     score = simulation_engine. calculate_performance(student)

        #     # Create and save test result
        #     test_result = TestResult(student_id=student.id, score=score)
        #     db.session.add(test_result)   

        #     # Add result to the response
        #     results.append({
        #         'student_id': student.id,
        #         'score': score,
        #         'university': student.university_id
        #     })
        #     # Commit changes
        #     db.session.commit()
        #     return jsonify({'status': 'success', 'results': results})
    # except Exception as e:
    #     print(f"Error processing student {student.id}: {str(e)}")  # Debugging
        


    # # Return results

    # except Exception as e:
    #     db.session.rollback()
    #     print(f"Simulation step error: {str(e)}")  # Debugging
    #     return jsonify({'status': 'error', 'message': str(e)}), 500


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

                          