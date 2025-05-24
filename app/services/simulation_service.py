""" Renders simulation charts to the frontend, process and run simulation """
from sqlalchemy.orm.collections import InstrumentedList
from .simulation_engine import SimulationEngine
from flask import jsonify
from .memory_state import create_memory_state



class SimulationService:
   """Running sinmulation and its services"""
   
   def __init__(self):
      from app.models import Simulation, Student
      self.sim_eng = SimulationEngine()
      self.sim_model = Simulation.query.all()
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

   def loader(self):
      return self.mem_loader
      
      
# processs factors
   def process_factors(self, factors, factor_type, identifier):
      """Process factors if they are an InstrumentedList."""
      try:
         if isinstance(factors, InstrumentedList):
            if factors:
               for factor in factors:
                  self.sim_eng.update_single_factor(factor)
                  print(f"{factor} processing")
            else:
               print(f"No {factor_type} found for {identifier}")
         else:
            # Handle single object case
            self.sim_eng.update_single_factor(factors)
      except Exception as e:
         raise RuntimeError(f"Error processing factors {str(e)}" )


# run simulation
   def process_simulation(self):
      """ process students in each simulation"""
      from app.models import InstitutionalFactors
      try:
         result = []
         simulations = self.sim_model         
         for simulation in simulations:
            students = simulation.students
            for student in students:
               if simulation.id == student.university_id:
                  try:            
                     # Processing each type of factors
                     university_factors = simulation.institutional_factors
                     self.process_factors(university_factors, "institutional factors", f"university {simulation.university_id}")
                     # print(university_factors)

                     external_factors = student.external_factors
                     self.process_factors(external_factors, "external factors", f"student {student.id}")
                     # print(external_factors)

                     internal_factors = student.internal_factors
                     self.process_factors(internal_factors, "internal factors", f"student {student.id}")
                     # print(internal_factors)

                     if not (student.external_factors and student.internal_factors and simulation.university_id):
                        print(f"Missing required data for student {student.id}")
                     
                     # Uncomment when ready
                     score = self.sim_eng.calculate_performance(student)

                     result.append({
                        'simulation_id': simulation.id, 
                        'student_id': student.id, 
                        # 'test': 1
                        'score': score
                     })
                  except Exception as e:
                     # raise RuntimeError( e)
                     # error status.
                     result.append({
                        'simulation_id': simulation.id,
                        'student_id': student.id,
                        'error': str(e)
                     })
               else:
                  print(f"No matching simulation found for student {student.id}")
         
         
         return {'status':'success' , 'result': result}
         
      except Exception as e:
         # return jsonify({'status': 'error', 'message': str(e)})
         raise RuntimeError(f"Error processingg simulation {str(e)}")