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
            if factors:
               for factor in factors:
                  self.sim_eng.update_single_factor(factor)
                  # print(f"{factor} processing")
            else:
               print(f"No {factor_type} found for {identifier}")
      except Exception as e:
         raise RuntimeError(f"Error processing factors {str(e)}" )


# run simulation
   def process_simulation(self, simulation_data):
      """ process students in each simulation"""
      from app.models import InstitutionalFactors
      try:
         result =[]
         simulations = self.sim_model

         for simulation in simulations:

            for simulation_id , internal_factors  in simulation_data.mem_internal_factors.items():
               if simulation_id == simulation.id:
                  self.process_factors(internal_factors, "internal factors", f"internal factor {simulation.id}")
                  
            for simulation_id , external_factors  in simulation_data.mem_external_factors.items():
               if simulation_id == simulation.id:
                  self.process_factors(external_factors, "external factors", f"external factor {simulation.id}")

            for simulation_id , institutional_factors  in simulation_data.mem_internal_factors.items():
               if simulation_id == simulation.id:
                  self.process_factors(institutional_factors, "external factors", f"external factor {simulation.id}")
                  
            
                  # Uncomment when ready
            score = self.sim_eng.calculate_performance(simulation_data)

            result.append({
               'simulation_id': simulation.id, 
               'score': score
            })
         
   
         return {'status':'success' , 'result': result}  
         
      except Exception as e:
         result.append({
            'simulation_id': simulation.id,
            # 'student_id': student.id,
            'error': str(e)
         })

         # return jsonify({'status': 'error', 'message': str(e)})
         raise f"Error processingg simulation {str(e)}"