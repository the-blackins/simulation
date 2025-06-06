import redis
import pickle

# establishing a connection to the Redis server
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# store date in Redis
def cache_simulation_data(data):
    serialized_data = pickle.dumps(data)
    redis_client.set('simulation_data', serialized_data)
    print("Simulation data cached successfully.")

# retrieve and return stored data from Redis 
def get_cached_simulation_data():
    serialized_data = redis_client.get('simulation_data')
    print("Retrieving cached simulation data...")

    if serialized_data:
        return pickle.loads(serialized_data)

    else:
        return None
    
def cache_lookup_data(mem_factor, mem_factor_identifier):
    """cache mem factor lookup data"""
    try:

        serialized_data = pickle.dumps(mem_factor)
        redis_client.set(mem_factor_identifier, serialized_data)
        print(f"successfully cached: {mem_factor_identifier}")
    except Exception as e:
        raise RuntimeError(f"Error caching lookup data: {str(e)}")
    
def get_cached_lookup_data(mem_factor_identifier):
    try:

        serialized_data = redis_client.get(mem_factor_identifier)

        print("Retrieving cahed lookup data...")
        if serialized_data:
            return pickle.loads(serialized_data)
    
    except Exception as e:
        raise RuntimeError(f"Error retrieving cached lookup data: {str(e)}")

        

