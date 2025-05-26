from .memory_state import state_wrapper
from .loader import load_initial_data
from .simulation_service import SimulationService


def loader():
    """loads data from the database"""
    mem_loader = load_initial_data()
    return mem_loader

def memory_state_population(simulation_data):
    """ initializes the memory state by loading data gotten from the database"""
    print(state_wrapper(simulation_data))


def main():

    
    loaded_data = loader()
    memory_state= memory_state_population(loaded_data)

    simulation_service = SimulationService()
    simulation_service.process_simulation(memory_state)


    




