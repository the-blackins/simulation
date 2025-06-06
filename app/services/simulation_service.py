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
      from app import db
      self.sim_eng = SimulationEngine()
      self.sim_model = (db.session.query(Simulation).join(Simulation.students)).all()
      
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
               print(f"Processed {count} {factor_type} for {identifier}")
                  # print(f"{factor} processing")
            else:
               print(f"No {factor_type} found for {identifier}")
      except Exception as e:
         raise RuntimeError(f"Error processing factors {str(e)}" )

   # helper funtion
   def build_lookup(self, mem_factor, mem_factor_identitier):
      """Helper function to help lookup of simulation id and student id"""
      try: 
         print("starting lookup...")
         count = 0  
         internal_flat_lookup: Dict[Tuple[int, int], Any] = {}
         external_flat_lookup: Dict[Tuple[int, int], Any] = {}
         institutional_flat_lookup: Dict[Tuple[int, int], Any] = {}

         if mem_factor_identitier == "mem_internal_factor":
            for (simulation_id , student_ids), values in mem_factor.items():
               for value in values:
                  for student_id in student_ids:
                     if student_id == value.id:
                        internal_flat_lookup[simulation_id, student_id] = value
                        count += 1
            
            print(" internal flat lookup fully loaded")
            return internal_flat_lookup
         
         if mem_factor_identitier == "mem_external_factor":
            for (simulation_id , student_ids), values in mem_factor.items():
               for value in values:
                  for student_id in student_ids:
                     if student_id == value.id:
                        external_flat_lookup[simulation_id, student_id] = value
                        count += 1
            
            print("external factors flat lookup fully loaded")
            return external_flat_lookup

         if mem_factor_identitier == "mem_institutional_factor":
            for (simulation_id , student_ids), values in mem_factor.items():
               for value in values:
                  for student_id in student_ids:
                     if student_id == value.id:
                        institutional_flat_lookup[simulation_id, student_id] = value
                        count += 1
            
            print("institutional flat lookup fully loaded")
            return institutional_flat_lookup

      except Exception as e:
         raise RuntimeError(f"Error during lookup of factors: {str(e)}")


# run simulation
   def process_simulation(self, simulation_data):
      """ process students in each simulation"""

      value = self.build_lookup(simulation_data.mem_internal_factors, mem_factor_identitier="mem_internal_factor")
      
      try:
         result =[]
         simulations = self.sim_model
         
         print(simulations)
         for simulation in simulations:
            print(simulation.id)
            for student in simulation.students:

               key = (simulation.id, student.id)
               print(f"Processing simulation {simulation.id} for student {student.id}")   
               
               looked_up_data = value.get(key)
               print(looked_up_data)
      
               if looked_up_data:
                  print(f"Processing internal factors for simulation {simulation.id}")
                  self.process_factors(looked_up_data, "internal factors", f"internal factor {simulation.id}")
               else:
                  print(f"No internal factors found for simulation {simulation.id}")
               print(looked_up_data)
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