""" Renders simulation charts to the frontend, process and run simulation """
from sqlalchemy.orm.collections import InstrumentedList
from .simulation_engine import SimulationEngine
from app.services.cache import get_cached_lookup_data




class SimulationService:
   """Running sinmulation and its services"""
   
   def __init__(self):
      from app.models import Simulation, Student
      from app import db
      self.sim_eng = SimulationEngine()
      self.sim_model = (db.session.query(Simulation).join(Simulation.students).order_by(Simulation.id)).all()
      self.student_model = Student.query.all()
 

   def chart_instance(self):
      available_simulations = self.sim_model
      try:
         chart_arr = []
         if available_simulations:
            for simulation_data in available_simulations:
               dictionary = {
                     "simulation_id" : simulation_data.id, 
                     "university": simulation_data.university.name,
                     "factors":{
                        "Internal_Factor": [], 
                        "External_Factor": [], 
                        "Institutional_Factor": []
                     }
               }
               
               chart_arr.append(dictionary)

         return chart_arr

      except Exception as e:
         raise   RuntimeError( f'An error occured {e}')     
      
# processs factors
   def process_factors(self, factor, factor_type, identifier):
      """Process factors if they are an InstrumentedList."""
      try:  
            count = 0
            if factor:
               
               self.sim_eng.update_single_factor(factor)
               count += 1
               # print(f"Processed {count} {factor_type} for {identifier}")
                  # print(f"{factor} processing")
            else:
               print(f"No {factor_type} found for {identifier}")
      except Exception as e:
         raise RuntimeError(f"Error processing factors {str(e)}" )


# run simulation
   def process_simulation(self):
      """ process students in each simulation"""
      internal_factor_data_lookup = get_cached_lookup_data(mem_factor_identifier="mem_internal_factor")
      external_factor_data_lookup = get_cached_lookup_data(mem_factor_identifier="mem_external_factor")
      institutional_factor_data_lookup = get_cached_lookup_data(mem_factor_identifier="mem_institutional_factor")

      try:
         result =[]
         simulations = self.sim_model
         
         # print(simulations)
         for simulation in simulations:
            # print(simulation.id)
            for student in simulation.students:

               key = (simulation.id, student.id)
               # print(f"Processing simulation {simulation.id} for student {student.id}")  z 
               
               # internal factors 
               internal_factor_looked_up_data = internal_factor_data_lookup.get(key)
               # print(internal_factor_looked_up_data)
      
               if internal_factor_looked_up_data:
                  # print(f"Processing internal factors for simulation {simulation.id}")
                  self.process_factors(internal_factor_looked_up_data, "internal factors", f"internal factor {simulation.id}")
               else:
                  print(f"No internal factors found for simulation {simulation.id}")
               # print(internal_factor_looked_up_data)

               # external factors
               external_factor_looked_up_data = external_factor_data_lookup.get(key)
               if external_factor_looked_up_data:
                  # print(f"Processing external factors for simulation {simulation.id}")
                  self.process_factors(external_factor_looked_up_data, "external factors", f"external factor {simulation.id}")
               else:
                  print(f"No external factors found for simulation {simulation.id}")
               
               # institutional factors 
               institutional_factor_looked_up_data = institutional_factor_data_lookup.get(key)
               if institutional_factor_looked_up_data:
                  # print(f"Processing institutional factors for simulation {simulation.id}")
                  self.process_factors(institutional_factor_looked_up_data, "institutionsl factors", f"institutional factor {simulation.id}")
               else:
                  print(f"No institutional factors found for simulation {simulation.id}")
            


            
               # Uncomment when ready
               score = self.sim_eng.calculate_performance(mem_internal_factors=internal_factor_looked_up_data , mem_external_factors=external_factor_looked_up_data, mem_institutional_factors=institutional_factor_looked_up_data)

               # print(score)
               result.append({ 
                  'simulation_id': simulation.id, 
                  'Student_id': student.id,
                  'score': score
               })
         
         return result
         
      except Exception as e:
         result.append({ # type: ignore
            'simulation_id': simulation.id, # type: ignore
            'Student_id': student.id,
            'error': str(e)
         })

         # return jsonify({'status': 'error', 'message': str(e)})
         raise f"Error processingg simulation {str(e)}" # type: ignore