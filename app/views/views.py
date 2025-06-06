import json

import traceback
from sqlalchemy.orm import Session
from datetime import datetime
from app.services.cache import cache_simulation_data, get_cached_simulation_data

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)

from app.services.simulation_service import SimulationService
from app.services import  loader

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

@form_bp.route('/submit-simulation', methods=['POST'])
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

    
        # Log simulation details
        print(f"Simulation created with: students={data['numStudents']}, "
              f"simulations={data['numSimulations']}, level={data['finalLevel']}, universities={data['universities']}")
        return redirect(url_for('form.load_memory'))
        
    except Exception as e:
        print("Server error:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500
 


@form_bp.route('/load-memory', methods = ['GET'])
def load_memory():
    """Load initial data into memory for simulation."""
    try:       
        # Load initial data from the database
        from app.services import  initialize_memory

        simulation_data = initialize_memory()
        cache_simulation_data(simulation_data)
        print("Simulation data loaded into cache successfully.")

        
        return redirect(url_for('form.build_flat_lookup'))
              
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f'Error: {str(e)}', 500
    
@form_bp.route('/build-lookup', methods=['GET'])
def build_flat_lookup():
    """Build flat lookup from the simulation data"""
    try:     
        from app.services import mem_factors_flat_lookup
        mem_factors_flat_lookup()

        return jsonify({
                'status': 'success',
                'message': 'Simulation created successfully',
                'redirect_url': url_for('simulate.simulation_page',  _external=True)
            }), 200 
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': f'Error building flat lookup: {str(e)}'}), 500
    
@simulate_bp.route('/simulate')
def simulation_page():
    try:       
        
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

        # Retrieve simulation data from cache
        simulation_data = get_cached_simulation_data()
        if not simulation_data:
            # If cache is empty, load from database
            simulation_data = loader.load_simulation_data(session)
            cache_simulation_data(simulation_data)  # Cache the loaded data
            print("Simulation data loaded from database and cached successfully.")

        print("simulation data retrieved from cache successfully.")
        # run the simulation step
        run_simulation()
        return jsonify({'status': 'success', 'message': 'Simulation step completed successfully.'}), 200
    
    except Exception as e:
        print(f"Error running simulation step: {str(e)}")
        return jsonify(f'error {str(e)}'), 500
    