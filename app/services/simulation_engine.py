import random
from sqlalchemy.orm.collections import InstrumentedList
from dataclasses import asdict

# from app.services.memory_state import create_memory_state


class SimulationEngine:
    def __init__(self):
        self.BASE_SCORE = 70
        self.RANDOM_VARIATION = 5
        self.FACTOR_WEIGHTS = {
            'external': 0.30,
            'internal': 0.40,
            'institutional': 0.30
        }
        self.EXCLUDED_ATTRIBUTES = ['id', 'student_id', 'university_id', 'simulation_id']
        

    def random_walk(self, obj, step_size ):
        """Apply random walk to factor values within bounds"""
        data_obj = vars(obj)
        for attr, value in data_obj.items():
            if attr not in self.EXCLUDED_ATTRIBUTES:
                if isinstance(value, float):
                    delta = random.uniform(-step_size, step_size)
                    new_value = value + delta 
                    setattr(obj, attr, new_value)
                    # print(f"Updated {attr} from {value} to {new_value}")
                else:
                    print(f"Skipping non-float attribute: {attr} with value {value}")

    def update_single_factor(self, factor_values_list_all):
        """update each attributes of the factor in the memory"""
        try:
            # factors = [state.institutional_factors,  state.internal_factors, state.external_factors]
            self.random_walk(factor_values_list_all, step_size=0.1)
                     
            
        except Exception as e:
            raise RuntimeError(f'error updating factors: {str(e)}') 
        
    
    def calculate_factor_impact(self, factors):
        """Calculate the weighted impact of a set of factors"""
        # If factors is a list/collection, use the first item
        # if isinstance(factors, SimulationState):
        if factors:
            factors = factors[0]  # Take the first item
        else:
            return 1.0  # Return default impact for empty list
        
        # Process single factor object
        total = 0
        count = 0
        for id, list_of_values in factors.items():
            factors[id] = [
                list(asdict(list_of_values).values() for factor in factors)
            ]
            for value in list_of_values:
                if type(value) == float:
                    total += list_of_values[count]
                    count += 1 
            
        return total / count if count > 0 else 1.0
    
     

    def calculate_performance(self, state):
        """Calculate student performance based on all factors"""
        # Handle potential None values or empty lists
        external_impact = (self.calculate_factor_impact(state.external_factors) 
                         if state.external_factors else 1.0)
        internal_impact = (self.calculate_factor_impact(state.internal_factors) 
                         if state.internal_factors else 1.0)
        institutional_impact = (self.calculate_factor_impact(state.institutional_factors) 
                              if state.institutional_factors else 1.0)

        weighted_impact = (
            external_impact * self.FACTOR_WEIGHTS['external'] +
            internal_impact * self.FACTOR_WEIGHTS['internal'] +
            institutional_impact * self.FACTOR_WEIGHTS['institutional']
        )

        random_variation = random.uniform(-self.RANDOM_VARIATION, self.RANDOM_VARIATION)
        final_score = self.BASE_SCORE * weighted_impact + random_variation

        return max(0, min(100, final_score))