import redis
import pickle
from log.logger import logger

# establishing a connection to the Redis server
redis_client = redis.Redis(host='localhost', port=6379, db=0)


# store data in Redis
def cache_simulation_data(data):
    try:
        serialized_data = pickle.dumps(data)
        redis_client.set('simulation_data', serialized_data)
        logger.info("Simulation data cached successfully.")
    except Exception as e:
        logger.error(f"Error caching simulation data: {str(e)}")
        raise RuntimeError(f"Error caching simulation data: {str(e)}")


# retrieve and return stored data from Redis
def get_cached_simulation_data():
    logger.debug("Retrieving cached simulation data...")
    try:
        serialized_data = redis_client.get('simulation_data')
        if serialized_data:
            logger.info("Cached simulation data retrieved successfully.")
            return pickle.loads(serialized_data)
        else:
            logger.warning("No cached simulation data found.")
            return None
    except Exception as e:
        logger.error(f"Error retrieving cached simulation data: {str(e)}")
        raise RuntimeError(f"Error retrieving cached simulation data: {str(e)}")


def cache_lookup_data(mem_factor, mem_factor_identifier):
    """Cache mem factor lookup data"""
    try:
        serialized_data = pickle.dumps(mem_factor)
        redis_client.set(mem_factor_identifier, serialized_data)
        logger.info(f"Successfully cached: {mem_factor_identifier}")
    except Exception as e:
        logger.error(f"Error caching lookup data for {mem_factor_identifier}: {str(e)}")
        raise RuntimeError(f"Error caching lookup data: {str(e)}")


def get_cached_lookup_data(mem_factor_identifier):
    try:
        logger.debug(f"Retrieving cached lookup data for {mem_factor_identifier}...")
        serialized_data = redis_client.get(mem_factor_identifier)
        if serialized_data:
            logger.info(f"Cached lookup data for {mem_factor_identifier} retrieved successfully.")
            return pickle.loads(serialized_data)
        else:
            logger.warning(f"No cached lookup data found for {mem_factor_identifier}.")
            return None
    except Exception as e:
        logger.error(f"Error retrieving cached lookup data for {mem_factor_identifier}: {str(e)}")
        raise RuntimeError(f"Error retrieving cached lookup data: {str(e)}")
