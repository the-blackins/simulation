""" Renders simulation charts to the frontend, process and run simulation """
from sqlalchemy.orm.collections import InstrumentedList
from .simulation_engine import SimulationEngine
from flask import jsonify
from .memory_state import create_memory_state
from dataclasses import asdict
from typing import Dict, Tuple, Any



class SimulationService:
   """Running sinmulation and its services"""
   
   def __init__(self):
      from app.models import Simulation, Student
      self.sim_eng = SimulationEngine()
      self.sim_model = Simulation.query.all()
      self.student_model = Student.query.all()
      # self.memory = create_memory_state()
      
      


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
               print(f"Processed {count} {factor_type} for {identifier}")
                  # print(f"{factor} processing")
            else:
               print(f"No {factor_type} found for {identifier}")
      except Exception as e:
         raise RuntimeError(f"Error processing factors {str(e)}" )

   # helper funtion
   def build_lookup(self, mem_factor):
      """Helper function to help lookup of simulation id and student id"""
      try: 
         print("starting lookup...")
         count = 0  
         flat_lookup: Dict[Tuple[int, int], Any] = {}
         for (simulation_id , student_ids), values in mem_factor.items():
            for value in values:
               for student_id in student_ids:
                  if student_id == value.id:
                     # print(f"simulation_id: {simulation_id}, student_id: {student_id}, value: {value}")
                     flat_lookup[simulation_id, student_id] = value
                     count += 1
         print("fully loaded")
         return flat_lookup
      except Exception as e:
         raise RuntimeError(f"Error during lookup of factors: {str(e)}")


# run simulation
   # import pdb; pdb.set_trace()
   def process_simulation(self, simulation_data):
      """ process students in each simulation"""

      value = self.build_lookup(simulation_data.mem_internal_factors)
      # print(value) 
      # print(simulation_data.mem_internal_factors)
      from app.models import InstitutionalFactors
      try:
         result =[]
         simulations = self.sim_model
         students = self.student_model
         
         

         count = 0
         for simulation in simulations:
            for student in students:

               key = (simulation.id, student.id)

               looked_up_data = value.get(key)
               print(looked_up_data)
      
               if looked_up_data:
                  print(f"Processing internal factors for simulation {simulation.id}")
                  self.process_factors(looked_up_data, "internal factors", f"internal factor {simulation.id}")
               else:
                  print(f"No internal factors found for simulation {simulation.id}")

               mem_external_factors = simulation_data.mem_external_factors.get(simulation.id)
               if mem_external_factors:
                  print(f"Processing external factors for simulation {simulation.id}")
                  self.process_factors(mem_external_factors, "external factors", f"external factor {simulation.id}")
               else:
                  print(f"No external factors found for simulation {simulation.id}")
               mem_institutional_factors = simulation_data.mem_institutional_factors.get(simulation.id)
               if mem_institutional_factors:
                  print(f"Processing institutional factors for simulation {simulation.id}")
                  self.process_factors(mem_institutional_factors, "institutionsl factors", f"institutional factor {simulation.id}")
               else:
                  print(f"No institutional factors found for simulation {simulation.id}")
            
               # Uncomment when ready
               score = self.sim_eng.calculate_performance(mem_internal_factors=value, mem_external_factors=mem_external_factors, mem_institutional_factors=mem_institutional_factors)

                  
               result.append({
                  'simulation_id': simulation.id, 
                  'score': score
               })
         
            print(result)
         # return {'status':'success' , 'result': result}  
         
      except Exception as e:
         result.append({ # type: ignore
            'simulation_id': simulation.id, # type: ignore
            
            'error': str(e)
         })

         # return jsonify({'status': 'error', 'message': str(e)})
         raise f"Error processingg simulation {str(e)}" # type: ignore