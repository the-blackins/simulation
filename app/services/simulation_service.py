""" Renders simulation charts to the frontend, process and run simulation """
import eventlet
eventlet.monkey_patch()
from sqlalchemy.orm.collections import InstrumentedList
from .simulation_engine import SimulationEngine
from app.services.cache import get_cached_lookup_data, cache_lookup_data
from log.logger import logger
from sqlalchemy.orm import joinedload

import time
from flask_socketio import emit, SocketIO

class SimulationService:
    """Running simulation and its services"""
   
    def __init__(self):
        from app.models import Simulation, Student
        from app import db
        self.sim_eng = SimulationEngine()
        self.sim_model = (db.session.query(Simulation).options(joinedload(Simulation.students)).join(Simulation.students).order_by(Simulation.id)).all()
        self.student_model = Student.query.all()
        logger.info("SimulationService initialized with simulation and student models.")
 
    def chart_instance(self):
        available_simulations = self.sim_model
        try:
            chart_arr = []
            if available_simulations:
                for simulation_data in available_simulations:
                    dictionary = {
                        "simulation_id": simulation_data.id, 
                        "university": simulation_data.university.name,
                        "factors": {
                            "Internal_Factor": [], 
                            "External_Factor": [], 
                            "Institutional_Factor": []
                        }
                    }
                    chart_arr.append(dictionary)
                logger.info(f"Prepared chart instance array with {len(chart_arr)} entries.")
            else:
                logger.warning("No available simulations found during chart_instance call.")
            return chart_arr

        except Exception as e:
            logger.error(f"An error occurred in chart_instance: {e}")
            raise RuntimeError(f'An error occurred {e}')     
      
    # process factors
    def process_factors(self, factor, factor_type, identifier):
        """Process factors if they are an InstrumentedList."""
        try:  
            if factor:
                self.sim_eng.update_single_factor(factor)
               #  logger.info(f"Processed {count} {factor_type} for {identifier}")
            else:
                logger.warning(f"No {factor_type} found for {identifier}")
        except Exception as e:
            logger.error(f"Error processing factors for {identifier}: {str(e)}")
            raise RuntimeError(f"Error processing factors {str(e)}")

    # run simulation
    def process_simulation(self, simulation):
        """ Process students in each simulation """
        try:
            internal_factor_data_lookup = get_cached_lookup_data(mem_factor_identifier="mem_internal_factor")
            external_factor_data_lookup = get_cached_lookup_data(mem_factor_identifier="mem_external_factor")
            institutional_factor_data_lookup = get_cached_lookup_data(mem_factor_identifier="mem_institutional_factor")

            result = []
            # simulations = self.sim_model
            factors = {
                    "simulation_id": None, 
                    "Internal_Factor": [], 
                    "External_Factor": [], 
                    "Institutional_Factor": []
            }
            avg_factors= []
            # for simulation in simulations:

            for student in simulation.students:
                # logger.info(f"Processing student {student.id} in simulation {simulation.id}")
                factors["simulation_id"] = simulation.id

                key = (simulation.id, student.id)
                  #   logger.debug(f"Processing simulation {simulation.id} for student {student.id}")

                # internal factors 
                internal_factor_looked_up_data = internal_factor_data_lookup.get(key)
                if internal_factor_looked_up_data:
                    # logger.info(f"Processing internal factors for simulation {simulation.id}")
                    factors['Internal_Factor'].append(self.sim_eng.calculate_factor_impact(internal_factor_looked_up_data))
                    # logger.info(f"not modified: {internal_factor_looked_up_data}")
                    self.process_factors(internal_factor_looked_up_data, "internal factors", f"internal factor {simulation.id}")
                    # logger.info(f"Modified: {internal_factor_looked_up_data}")

                else:
                    logger.warning(f"No internal factors found for simulation {simulation.id}")

                # external factors
                external_factor_looked_up_data = external_factor_data_lookup.get(key)
                if external_factor_looked_up_data:
                    factors['External_Factor'].append(self.sim_eng.calculate_factor_impact(external_factor_looked_up_data))

                    # logger.info(f"Processing external factors for simulation {simulation.id}")
                    self.process_factors(external_factor_looked_up_data, "external factors", f"external factor {simulation.id}")
                else:
                    logger.warning(f"No external factors found for simulation {simulation.id}")
                
                # institutional factors 
                institutional_factor_looked_up_data = institutional_factor_data_lookup.get(key)
                if institutional_factor_looked_up_data:
                    factors["Institutional_Factor"].append(self.sim_eng.calculate_factor_impact(institutional_factor_looked_up_data))

                    # logger.info(f"Processing institutional factors for simulation {simulation.id}")
                    self.process_factors(institutional_factor_looked_up_data, "institutional factors", f"institutional factor {simulation.id}")
                else:
                    logger.warning(f"No institutional factors found for simulation {simulation.id}")

                # calculate score
                score = self.sim_eng.calculate_performance(
                    mem_internal_factors=internal_factor_looked_up_data,
                    mem_external_factors=external_factor_looked_up_data,
                    mem_institutional_factors=institutional_factor_looked_up_data
                )
                logger.debug(f"Calculated score for simulation {simulation.id}, student {student.id}: {score}")

                result.append({ 
                    'simulation_id': simulation.id, 
                    'Student_id': student.id,
                    'score': score
                })
            avg_factors.append({
                "simulation_id" : factors["simulation_id"],
                "avg_internal_factor" : sum(factors["Internal_Factor"])/len(factors["Internal_Factor"]), 
                "avg_external_factor" : sum(factors["External_Factor"])/len(factors["External_Factor"]), 
                "avg_institutional_factor" : sum(factors["Institutional_Factor"])/len(factors["Institutional_Factor"])  
            })
            # update cached lookup data
            cache_lookup_data(internal_factor_data_lookup, mem_factor_identifier="mem_internal_factor")
            cache_lookup_data(external_factor_data_lookup, mem_factor_identifier="mem_external_factor")
            cache_lookup_data(institutional_factor_data_lookup, mem_factor_identifier="mem_institutional_factor")   
            # logger.info(factors)
            result.append(avg_factors)
            logger.info(f"Completed processing simulations id {simulation.id} for {len(result)} students.") 
            return result


            

        except Exception as e:
            logger.error(f"Error processing simulation {simulation.id} for student {student.id}: {str(e)}")
            result.append({# type: ignore
                'simulation_id': simulation.id,  # type: ignore
                'Student_id': student.id,
                'error': str(e)
            })
            raise RuntimeError(f"Error processing simulation {str(e)}")  # type: ignore
    
   