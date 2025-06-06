# helper funtion
from typing import Dict, Tuple, Any

def build_lookup(mem_factor, mem_factor_identitier):
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
            
            print(" internal flat lookup fully loaded")
            return internal_flat_lookup
        
        if mem_factor_identitier == "mem_external_factor":
            for (simulation_id , student_ids), values in mem_factor.items():
                for value in values:
                    for student_id in student_ids:
                        if student_id == value.id:
                            external_flat_lookup[simulation_id, student_id] = value
            
            print("external factors flat lookup fully loaded")
            return external_flat_lookup

        if mem_factor_identitier == "mem_institutional_factor":
            for (simulation_id , student_ids), values in mem_factor.items():
                for student_id in student_ids:
                    for value in values:
                        print(value)
                        if simulation_id == value.id:
                            institutional_flat_lookup[simulation_id, student_id] = value
         
            print("institutional flat lookup fully loaded")
            return institutional_flat_lookup
    except Exception as e:
         raise RuntimeError(f"Error during lookup of factors: {str(e)}")