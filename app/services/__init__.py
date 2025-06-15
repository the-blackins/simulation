from .memory_state import state_wrapper
from .loader import load_initial_data
from .simulation_service import SimulationService
from app.services.cache import get_cached_simulation_data, cache_lookup_data
from app.utils.build_flat_lookup import build_lookup
from log.logger import logger


def loader():
    """Loads data from the database."""
    return load_initial_data()


def memory_state_population(simulation_data):
    """Initializes the memory state by loading data gotten from the database."""
    return state_wrapper(simulation_data)


def load_memory():
    """Runs the simulation by loading data from the database and processing it."""
    logger.info("Starting memory population...")
    try:
        loaded_data = loader()
        memory_state = memory_state_population(loaded_data)
        logger.info("Memory initialized and populated successfully.")
        return memory_state
    except Exception as e:
        logger.exception("Failed to load and initialize memory.")
        raise


def initialize_memory():
    """Initialize memory within app context."""
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            logger.info("Loading initial data...")
            initial_data = loader()
            logger.info("Initial data loaded successfully.")

            logger.info("Creating memory state...")
            simulation_data = memory_state_population(initial_data)
            logger.info("Memory state created successfully.")

            return simulation_data
        except Exception as e:
            logger.exception("Error during memory initialization.")
            raise


def mem_factors_flat_lookup():
    """Build flat lookup for each memory factor type and cache the result."""
    try:
        simulation_data = get_cached_simulation_data()
        if not simulation_data:
            logger.warning("No simulation data found in cache. Please load memory first.")
            raise RuntimeError("No simulation data found in cache. Please load memory first.")

        logger.info("Building flat lookup for memory factors...")

        internal_factor_data = simulation_data.mem_internal_factors
        internal_factors_flat_lookup = build_lookup(
            mem_factor=internal_factor_data, mem_factor_identitier="mem_internal_factor"
        )
        cache_lookup_data(internal_factors_flat_lookup, mem_factor_identifier="mem_internal_factor")

        institutional_factor_data = simulation_data.mem_institutional_factors
        institutional_factors_flat_lookup = build_lookup(
            mem_factor=institutional_factor_data, mem_factor_identitier="mem_institutional_factor"
        )
        cache_lookup_data(institutional_factors_flat_lookup, mem_factor_identifier="mem_institutional_factor")

        external_factor_data = simulation_data.mem_external_factors
        external_factors_flat_lookup = build_lookup(
            mem_factor=external_factor_data, mem_factor_identitier="mem_external_factor"
        )
        cache_lookup_data(external_factors_flat_lookup, mem_factor_identifier="mem_external_factor")

        logger.info("Flat lookup built and cached successfully.")
        return "Flat lookup built and cached successfully."

    except Exception as e:
        logger.exception("Failed to build flat lookup.")
        raise


def run_simulation():
    """Runs the simulation by processing cached data."""
    simulation_service = SimulationService()
    try:
        logger.info("Processing simulation...")
        simulation_service.start_simulation_threading()
        processed_simulation = simulation_service.process_simulation()
        logger.info("Simulation run successfully.")
        return processed_simulation
    except Exception as e:
        logger.exception("Error occurred during simulation run.")
        return str(e)
