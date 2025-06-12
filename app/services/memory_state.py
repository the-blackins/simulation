"""Memory state of the in-memory models"""

from app.services.loader import load_initial_data
from app.services.model_representation import SimulationState
from app.services.model_representation import MemInstitutionalFactor, MemInternalFactor, MemExternalFactor
from typing import Dict
from collections import defaultdict
from log.logger import logger  # Assuming logger is already configured


def hold_current_state(state):
    logger.debug("Holding current memory state.")
    return state


def create_memory_state(mem_dict):
    """Process db_objects and return a SimulationState instance."""
    from app.models import InstitutionalFactors, InternalFactors, ExternalFactors, Simulation

    try:
        logger.debug("Creating memory state from simulation data...")
        mem_institutional_factors = defaultdict(list)
        mem_external_factors = defaultdict(list)
        mem_internal_factors = defaultdict(list)

        for f in mem_dict.get("institutional_factors", []):
            student_ids = tuple(student.id for student in f.simulation.students)
            mem_institutional_factors[(f.simulation.id, student_ids)].append(
                MemInstitutionalFactor(
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
            )

        for f in mem_dict.get("internal_factors", []):
            student_ids = tuple(student.id for student in f.simulation.students)
            mem_internal_factors[(f.simulation.id, student_ids)].append(
                MemInternalFactor(
                    id=f.id,
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
            )

        for f in mem_dict.get("external_factors", []):
            student_ids = tuple(student.id for student in f.simulation.students)
            mem_external_factors[(f.simulation.id, student_ids)].append(
                MemExternalFactor(
                    id=f.id,
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
            )

        logger.info("Memory state created successfully for wsimulation.")
        return SimulationState(
            mem_internal_factors=mem_internal_factors,
            mem_external_factors=mem_external_factors,
            mem_institutional_factors=mem_institutional_factors
        )

    except Exception as e:
        logger.exception("Error creating memory state from database objects.")
        raise RuntimeError(f"Error creating memory state: {str(e)}")


def merge_state(base: SimulationState, new: SimulationState):
    logger.debug("Merging new memory state into the base state...")
    for k, v in new.mem_internal_factors.items():
        base.mem_internal_factors[k].extend(v)

    for k, v in new.mem_external_factors.items():
        base.mem_external_factors[k].extend(v)

    for k, v in new.mem_institutional_factors.items():
        base.mem_institutional_factors[k].extend(v)

    logger.info("Memory state merge completed.")
    return base


def state_wrapper(mem_list):
    try:
        logger.info("Wrapping simulation data into memory state...")
        accumated_state = SimulationState(
            mem_internal_factors=defaultdict(list),
            mem_external_factors=defaultdict(list),
            mem_institutional_factors=defaultdict(list)
        )

        for mem_dict in mem_list:
            mermory_state = create_memory_state(mem_dict)
            accumated_state = merge_state(accumated_state, mermory_state)

        logger.info("All memory states wrapped successfully.")
        return accumated_state

    except Exception as e:
        logger.exception("Error wrapping states.")
        raise RuntimeError("Error wrapping states")
