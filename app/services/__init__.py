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


def run_simulation():
    """runs the simulation by loading data from the database and processing it"""
    updated_memory = load_memory()
    print("simulation service test...")
    simulation_service = SimulationService()
    print("Processing simulation...")
    simulation_service.process_simulation(updated_memory)
    print("Simulation run successfully")





    




