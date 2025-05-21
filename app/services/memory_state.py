""" memory state of the in-memory models"""

from app.services.loader import load_initial_data
from app.services.model_representation import SimulationState
from sqlalchemy.orm import session

initial_data= load_initial_data()
simulation_state = SimulationState()

class States:
    def __init__(self, states,):
        self.states = states
        

    def create_memory_state(self, db_objects):
        from app.models import InstitutionalFactors, InternalFactors, ExternalFactors, Simulation
        

        """Process db_objects and return a SimulationState instance."""
        try:
            model_state = SimulationState( 
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
                # institutional factor, would be related to the simulation. 
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
            return model_state
            
        except Exception as e:
        
            raise f"error processing  database objects as {str(e)}"


    def state_wrapper(self):
        from app import db
        from app.models import Simulation
        try:
            with db.session.no_autoflush:
                # get the total number of simulations in the simulation  database

                simulations =Simulation.query.all()
                for simulation in simulations:
                    mermory_state= self.create_memory_state(db_objects)
                    sim_states = States(mermory_state)
                return sim_states
        except Exception as e:
            raise RuntimeError(f"error wrapping states ")

        