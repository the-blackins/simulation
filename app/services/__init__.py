from .memory_state import state_wrapper
from .loader import load_initial_data
from .simulation_service import SimulationService


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
    
def run_simulation(simulation_data):
    """runs the simulation by loading data from the database and processing it"""
    simulation_service = SimulationService()
    print("Processing simulation...")
    simulation_service.process_simulation(simulation_data)
    print("Simulation run successfully")





    




