import random
from sqlalchemy.orm.collections import InstrumentedList

class SimulationEngine:
    def __init__(self):
        self.BASE_SCORE = 70
        self.RANDOM_VARIATION = 5
        self.FACTOR_WEIGHTS = {
            'external': 0.30,
            'internal': 0.40,
            'institutional': 0.30
        }

    def random_walk(self, current_value):
        """Apply random walk to factor values within bounds"""
        delta = random.uniform(-0.1, 0.1)
        new_value = current_value + delta
        return max(0.5, min(1.5, new_value))

    def update_factors(self, factors):
        """Update all factors using random walk"""
        from app.models import InternalFactors, ExternalFactors, InstitutionalFactors
        
        # If factors is a list/collection, process the first item
        if isinstance(factors, InstrumentedList):
            if factors:
                factors = factors[0]  # Take the first item
            else:
                return  # Empty list, nothing to process
        
        # Process single factor object
        if isinstance(factors, (InternalFactors, ExternalFactors, InstitutionalFactors)):
            for column in factors.__table__.columns:
                if column.name not in ['id', 'student_id', 'university_id']:
                    current_value = getattr(factors, column.name)
                    setattr(factors, column.name, self.random_walk(current_value))
        else:
            print(f"Warning: {factors} is not a valid SQLAlchemy model instance.")

    def calculate_factor_impact(self, factors):
        """Calculate the weighted impact of a set of factors"""
        # If factors is a list/collection, use the first item
        if isinstance(factors, InstrumentedList):
            if factors:
                factors = factors[0]  # Take the first item
            else:
                return 1.0  # Return default impact for empty list
        
        # Process single factor object
        total = 0
        count = 0
        for column in factors.__table__.columns:
            if column.name not in ['id', 'student_id', 'university_id']:
                total += getattr(factors, column.name)
                count += 1
        return total / count if count > 0 else 1.0

    def calculate_performance(self, student):
        """Calculate student performance based on all factors"""
        # Handle potential None values or empty lists
        external_impact = (self.calculate_factor_impact(student.external_factors) 
                         if student.external_factors else 1.0)
        internal_impact = (self.calculate_factor_impact(student.internal_factors) 
                         if student.internal_factors else 1.0)
        institutional_impact = (self.calculate_factor_impact(student.university.institutional_factors) 
                              if student.university and student.university.institutional_factors else 1.0)

        weighted_impact = (
            external_impact * self.FACTOR_WEIGHTS['external'] +
            internal_impact * self.FACTOR_WEIGHTS['internal'] +
            institutional_impact * self.FACTOR_WEIGHTS['institutional']
        )

        random_variation = random.uniform(-self.RANDOM_VARIATION, self.RANDOM_VARIATION)
        final_score = self.BASE_SCORE * weighted_impact + random_variation

        return max(0, min(100, final_score))