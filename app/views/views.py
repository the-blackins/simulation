import json
import traceback
from sqlalchemy.orm import Session
from datetime import datetime
from app.services.cache import cache_simulation_data, get_cached_simulation_data

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)

from app.services.simulation_service import SimulationService
from app.services import loader
from log.logger import logger

form_bp = Blueprint('form', __name__)
home_bp = Blueprint('home', __name__)
simulate_bp = Blueprint('simulate', __name__)


@home_bp.route('/', methods=['GET'])    
def landing_page():
    logger.debug("Rendering landing page.")
    return render_template('index.html')


@home_bp.route('/simulation-setup', methods=['GET'])
def simulation_setup():
    logger.debug("Rendering simulation setup form.")
    return render_template('form.html')


@form_bp.route('/submit-simulation', methods=['POST'])
def submit_simulation_form():
    try:         
        from database_population.seeds import seed_data
        data = request.get_json()
        
        if not data:
            logger.warning("No data provided in simulation form.")
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        required_fields = ['numStudents', 'numSimulations', 'finalLevel', 'universities']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        logger.info("Received simulation form data.")
        seed_data(data['universities'], data['numStudents'])

        logger.info(f"Simulation setup created: students={data['numStudents']}, "
                    f"simulations={data['numSimulations']}, level={data['finalLevel']}, "
                    f"universities={data['universities']}")
        
        return redirect(url_for('form.load_memory'))
        
    except Exception as e:
        logger.exception("An error occurred while submitting the simulation form.")
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


@form_bp.route('/load-memory', methods=['GET'])
def load_memory():
    """Load initial data into memory for simulation."""
    try:
        from app.services import initialize_memory

        logger.debug("Initializing memory with simulation data.")
        simulation_data = initialize_memory()
        cache_simulation_data(simulation_data)

        logger.info("Simulation data loaded into cache successfully.")
        return redirect(url_for('form.build_flat_lookup'))

    except Exception as e:
        logger.exception("An error occurred while loading memory.")
        return f'Error: {str(e)}', 500


@form_bp.route('/build-lookup', methods=['GET'])
def build_flat_lookup():
    """Build flat lookup from the simulation data"""
    try:
        from app.services import mem_factors_flat_lookup

        logger.debug("Building flat lookup from simulation data.")
        mem_factors_flat_lookup()

        logger.info("Flat lookup built successfully.")
        return jsonify({
            'status': 'success',
            'message': 'Simulation created successfully',
            'redirect_url': url_for('simulate.simulation_page', _external=True)
        }), 200

    except Exception as e:
        logger.exception("Error building flat lookup.")
        return jsonify({'status': 'error', 'message': f'Error building flat lookup: {str(e)}'}), 500


@simulate_bp.route('/simulate')
def simulation_page():
    try:
        logger.debug("Rendering simulation page.")
        return render_template('simulation.html'), 200

    except Exception as e:
        logger.exception("Error rendering simulation page.")
        return str(e), 500


@simulate_bp.route('/api/chart_render')
def load_chart_instance():
    simulation_service = SimulationService()
    try:
        logger.debug("Generating chart instance for simulation.")
        charts = simulation_service.chart_instance()
        logger.info("Chart instance generated successfully.")
        return jsonify({"data": charts})

    except Exception as e:
        logger.exception("Error generating chart instance.")
        return str(e)


@simulate_bp.route('/api/run_step', methods=['POST'])
def run_simulation_step():
    """Run the simulation based on university base (simulation)."""
    session = Session()

    try:
        from app.services import run_simulation

        logger.debug("Retrieving simulation data from cache.")
        simulation_data = get_cached_simulation_data()
        if not simulation_data:
            logger.info("Simulation cache empty. Loading from database.")
            simulation_data = loader.load_simulation_data(session)
            cache_simulation_data(simulation_data)
            logger.info("Simulation data loaded from database and cached.")

        logger.debug("Running simulation step.")
        result = run_simulation()

        logger.info("Simulation step completed successfully.")
        return jsonify({
            'status': 'success',
            'message': 'Simulation step completed successfully.',
            'result': result
        }), 200

    except Exception as e:
        logger.exception("Error running simulation step.")
        return jsonify(f'error {str(e)}'), 500
