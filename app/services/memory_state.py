""" memory state of the in-memory models"""

from app.services.loader import load_initial_data
from app.services.model_representation import SimulationState
from sqlalchemy.orm import session
from app.services.model_representation import MemInstitutionalFactor, MemInternalFactor, MemExternalFactor

# initial_data= load_initial_data()
# simulation_state = SimulationState()


def hold_current_state(state):
    current_state =  state
    return current_state
        

def create_memory_state( mem_dict):
    from app.models import InstitutionalFactors, InternalFactors, ExternalFactors, Simulation
    

    """Process db_objects and return a SimulationState instance."""
    try:
        
        mem_institutional_factors={
            f.simulation_id: MemInstitutionalFactor(
                id=f.id,
                class_size=f.class_size,
                facility_availability=f.facility_availability,
                peer_support=f.peer_support,
                academic_guidance=f.academic_guidance,
                financial_aid=f.financial_aid,
                extracurricular_opportunities=f.extracurricular_opportunities,
                cultural_norms=f.cultural_norms,
                peer_influence=f.peer_influence
            )
            for f in mem_dict.get("institutional_factors", [])
        }, 
        mem_internal_factors={
            f.id: MemInternalFactor(
                id=f.id,
                simulation_id= f.simulation_id,
                goal_setting=f.goal_setting,
                personal_ambition=f.personal_ambition,
                interest_subject=f.interest_subject,
                scheduling=f.scheduling,
                prioritization=f.prioritization,
                consistency=f.consistency,
                study_techniques=f.study_techniques,
                focus_study=f.focus_study,
                self_assessment=f.self_assessment
            )
            for f in mem_dict.get("internal_factors", [])

        }, 
        mem_external_factors={
            f.id: MemExternalFactor(
                id=f.id,
                simulation_id= f.simulation_id,
                financial_stability=f.financial_stability,
                family_expectations=f.family_expectations,  
                access_to_resources=f.access_to_resources,
                family_support=f.family_support,
                textbooks_availability=f.textbooks_availability,
                internet_access=f.internet_access,
                lab_materials=f.lab_materials,
                curriculum_relevance=f.curriculum_relevance,
                teaching_quality=f.teaching_quality,
                feedback_assessment=f.feedback_assessment
            )
            for f in mem_dict.get("external_factors", [])
        },

        model_state=  SimulationState( 
            # simulation id of which these tables are associated to 
            mem_internal_factors = mem_internal_factors,
            mem_external_factors = mem_external_factors,
            mem_institutional_factors =mem_institutional_factors
        )
        return model_state
        
    except Exception as e:
    
        raise f"error processing  database objects as {str(e)}"


def state_wrapper(mem_list):
    from app import db
    try:
        with db.session.no_autoflush:
            # get the total number of simulations in the simulation  database
            for mem_dict in mem_list:
                mermory_state= create_memory_state(mem_dict)
                sim_states = hold_current_state( mermory_state)
            return print(sim_states.mem_internal_factors)
    except Exception as e:
        raise RuntimeError(f"error wrapping states ")

    