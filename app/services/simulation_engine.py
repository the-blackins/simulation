import random
from sqlalchemy.orm.collections import InstrumentedList
from dataclasses import asdict
from log.logger import logger

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
        logger.debug("SimulationEngine initialized with base score %s and factor weights %s",
                     self.BASE_SCORE, self.FACTOR_WEIGHTS)

    def random_walk(self, obj, step_size):
        """Apply random walk to factor values within bounds"""
        data_obj = vars(obj)
        for attr, value in data_obj.items():
            if attr not in self.EXCLUDED_ATTRIBUTES:
                if isinstance(value, float):
                    delta = random.uniform(-step_size, step_size)
                    new_value = value + delta
                    setattr(obj, attr, new_value)
                    # logger.debug("Updated attribute '%s' from %f to %f", attr, value, new_value)
                else:
                    logger.info("Skipping non-float attribute: %s with value %s", attr, value)

    def update_single_factor(self, factor_values_list_all):
        """Update each attribute of the factor in the memory"""
        try:
            self.random_walk(factor_values_list_all, step_size=0.1)
            # logger.info("Updated single factor using random walk")
        except Exception as e:
            logger.error("Error updating factors: %s", str(e))
            raise RuntimeError(f'error updating factors: {str(e)}')

    def calculate_factor_impact(self, factor):
        """Calculate the weighted impact of a set of factor objects"""
        try:
            total = 0
            count = 0
            if factor:
                dict_factors = vars(factor)
                for attr, value in dict_factors.items():
                    if attr not in self.EXCLUDED_ATTRIBUTES:
                        total += value
                        count += 1
                logger.debug("Calculated factor impact: total=%f count=%d", total, count)
            else:
                logger.warning("Invalid factor object provided: %s", factor)
                return 1.0
            # logger.info(total / (count * 10) if count > 0 else 1.0)
            return total / (count) if count > 0 else 1.0
        except Exception as e:
            logger.error("Error calculating factor impact: %s", str(e))
            raise RuntimeError(f"error calculating factor impact: {str(e)}")

    def calculate_performance(self, mem_internal_factors, mem_external_factors, mem_institutional_factors):
        """Calculate student performance based on all factors"""
        try:
            external_impact = (self.calculate_factor_impact(mem_external_factors)
                               if mem_external_factors else 1.0)
            internal_impact = (self.calculate_factor_impact(mem_internal_factors)
                               if mem_internal_factors else 1.0)
            
            

            institutional_impact = (self.calculate_factor_impact(mem_institutional_factors)
                                    if mem_institutional_factors else 1.0)

            weighted_impact = (
                external_impact * self.FACTOR_WEIGHTS['external'] +
                internal_impact * self.FACTOR_WEIGHTS['internal'] +
                institutional_impact * self.FACTOR_WEIGHTS['institutional']
            )

            random_variation = random.uniform(-self.RANDOM_VARIATION, self.RANDOM_VARIATION)
            final_score = self.BASE_SCORE * weighted_impact + random_variation
            clamped_score = max(0, min(100, final_score))

            # # logger.info(
            #     "Calculated performance: external_impact=%.2f, internal_impact=%.2f, institutional_impact=%.2f, "
            #     "weighted_impact=%.2f, random_variation=%.2f, final_score=%.2f, clamped_score=%.2f",
            #     external_impact, internal_impact, institutional_impact, weighted_impact, random_variation, final_score, clamped_score)

            return clamped_score
        except Exception as e:
            logger.error("Error calculating performance: %s", str(e))
            raise RuntimeError(f"error calculating performance: {str(e)}")
