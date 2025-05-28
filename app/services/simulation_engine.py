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
        
    
    def calculate_factor_impact(self, factor):
        """Calculate the weighted impact of a set of factor objects"""
        try:
            # Process single factor object
        
            total = 0
            count = 0
            if factor:
                dict_factors = vars(factor)
                for attr, value in dict_factors.items():
                    if attr not in self.EXCLUDED_ATTRIBUTES:
                        total += value
                        count += 1
                        
            else:
                print(f'{factor} is not a valid object')

            return total / count if count > 0 else 1.0
        except Exception as e:
            raise (f"error calculating factor impact: {str(e)}")
     

    def calculate_performance(self, mem_internal_factors, mem_external_factors, mem_institutional_factors ):
        """Calculate student performance based on all factors"""
        try:
            # Handle potential None values or empty lists
            for mem_external_factor in mem_external_factors:
                external_impact = (self.calculate_factor_impact(mem_external_factor) 
                                if mem_external_factor else 1.0)
            
            for mem_internal_factor in mem_internal_factors:
                internal_impact = (self.calculate_factor_impact(mem_internal_factor) 
                                if  mem_internal_factor else 1.0)
            
            for mem_institutional_factor in mem_institutional_factors:
                institutional_impact = (self.calculate_factor_impact(mem_institutional_factor) 
                                    if mem_institutional_factor else 1.0)

            weighted_impact = (
                external_impact * self.FACTOR_WEIGHTS['external'] +
                internal_impact * self.FACTOR_WEIGHTS['internal'] +
                institutional_impact * self.FACTOR_WEIGHTS['institutional']
            )

            random_variation = random.uniform(-self.RANDOM_VARIATION, self.RANDOM_VARIATION)
            final_score = self.BASE_SCORE * weighted_impact + random_variation
            
            return final_score
        except Exception as e:
            raise RuntimeError(f"error calculating performance: {str(e)}")

        # return max(0, min(100, final_score))