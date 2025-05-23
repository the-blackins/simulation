import random
from sqlalchemy.orm.collections import InstrumentedList

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
        for attr, value in vars(obj).items():
            if attr not in self.EXCLUDED_ATTRIBUTES:
                if isinstance(value, float):
                    delta = random.uniform(-step_size, step_size)
                    new_value = value + delta
                    setattr(obj, attr, new_value)

    def update_single_factor(self, state):
        # from app import db

        # from app.models import InternalFactors, ExternalFactors, InstitutionalFactors
        # try:
        #     EXCLUDED_COLUMNS =['id', 'student_id', 'university_id', 'simulation_id']
        #     # Process single factor object
        #     if isinstance(factors, (InternalFactors, ExternalFactors, InstitutionalFactors)):
        #         for column in factors.__table__.columns:
        #             if column.name not in EXCLUDED_COLUMNS:
        #                 current_value = getattr(factors, column.name)
        #                 setattr(factors, column.name, self.random_walk(current_value))
        #     else:
        #         print(f"Warning: {factors} is not a valid SQLAlchemy model instance.")

        # except Exception as e:
        #     db.session.rollback()
        #     raise f"Error when processing factors: {str(e)}"
        """update each attributes of the factor in the memory"""
        try:
            factors = [state.institutional_factors,  state.internal_factors, state.external_factors]
            for factor in factors:
                for obj in factor.values():
                    self.random_walk(obj, step_size=0.1)
                     
            
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
        for attr, value in factors.items():
            if attr not in ['id', 'student_id', 'university_id', 'simulation_id']:
                total += value
                count += 1
        
        return total / count if count > 0 else 1.0
    
    """utilize this function to calculate the average facotor influence for each student
    """

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