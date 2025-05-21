""" memory state of the in-memory models"""

from app.services.loader import load_initial_data
from app.services.model_representation import SimulationState

initial_data= load_initial_data()
simulation_state = SimulationState()

def create_memory_state(db_objects):
    from app.models import InstitutionalFactors, InternalFactors, ExternalFactors

    """Process db_objects and return a SimulationState instance."""
    try:
        return SimulationState(
        institutional_factors={
            f.id: simulation_state.mem_institutional_factors(
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
            for f in db_objects if isinstance(f, InstitutionalFactors)
        }, 
        internal_factors={
            f.id: simulation_state.mem_internal_factors(
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
            for f in db_objects if isinstance(f, InternalFactors)
        }, 
        external_factors={
            f.id: simulation_state.mem_external_factors(
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
            for f in db_objects if isinstance(f, ExternalFactors)
        }
    )
    except Exception as e:
    
        raise f"error processing  database objects as {str(e)}"
    


    