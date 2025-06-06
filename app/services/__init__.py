from .memory_state import state_wrapper
from .loader import load_initial_data
from .simulation_service import SimulationService
from app.services.cache import get_cached_simulation_data, cache_lookup_data





def loader():
    """loads data from the database"""
    mem_loader = load_initial_data()
    return mem_loader

def memory_state_population(simulation_data):
    """ initializes the memory state by loading data gotten from the database"""
    
    return state_wrapper(simulation_data)


def load_memory():
    """runs the simulation by loading data from the database and processing it"""

    print("Populating memory...")
    # Load initial data from the database       
    loaded_data = loader()
    memory_state=memory_state_population(loaded_data)
    print("Memory initialized and populated successfully")
    return memory_state
# app/services/__init__.py

def initialize_memory():
    from app import create_app
    app = create_app()
    with app.app_context():
        print("Loading initial data...")
        initial_data = loader()
        print("Initial data loaded successfully")
        print("Creating memory state...")
        simulation_data = memory_state_population(initial_data)
        print("Memory state created successfully")
        return simulation_data

def mem_factors_flat_lookup():

        simulation_data = get_cached_simulation_data()
        simulation_service= SimulationService()

        print("Building flat lookup for memory factors...")
        if not simulation_data:
            raise RuntimeError("No simulation data found in cache. Please load memory first.")
        # Build flat lookup for each factor type
        internal_factor_data = simulation_data.mem_internal_factors
        internal_factors_flat_lookup = simulation_service.build_lookup(internal_factor_data, mem_factor_identitier="mem_internal_factor")
        cache_lookup_data(internal_factors_flat_lookup, mem_factor_identifier="mem_internal_factor")

        institutional_factor_data = simulation_data.mem_institutional_factors
        institutional_factors_flat_lookup = simulation_service.build_lookup(institutional_factor_data, mem_factor_identitier="mem_institutional_factor")
        cache_lookup_data(institutional_factors_flat_lookup, mem_factor_identifier="mem_institutional_factor" )
        

        external_factor_data = simulation_data.mem_external_factors
        external_factors_flat_lookup = simulation_service.build_lookup(external_factor_data, mem_factor_identitier="mem_external_factor")
        cache_lookup_data(external_factors_flat_lookup, mem_factor_identifier="mem_external_factor")
        return "Flat lookup built and cahed successfully"

def run_simulation(simulation_data):
    """runs the simulation by loading data from the database and processing it"""
    simulation_service = SimulationService()
    print("Processing simulation...")
    simulation_service.process_simulation(simulation_data)
    print("Simulation run successfully")





    




