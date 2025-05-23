"""model represention for in-memory simulation"""

from typing import Dict , List

from dataclasses import dataclass

@dataclass
class MemInternalFactor:
    id: int
    simulation_id: int
    goal_setting: float
    personal_ambition: float
    interest_subject: float
    scheduling: float
    prioritization: float
    consistency:float
    study_techniques:float
    focus_study:float
    self_assessment: float

@dataclass
class MemExternalFactor:
    id: int
    simulation_id: int
    family_expectations : float
    financial_stability : float
    access_to_resources : float
    family_support : float
    textbooks_availability : float
    internet_access : float
    lab_materials : float
    curriculum_relevance : float
    teaching_quality : float
    feedback_assessment : float


@dataclass
class MemInstitutionalFactor:
    id : int
    class_size : float
    facility_availability : float
    peer_support : float
    academic_guidance : float
    financial_aid : float
    extracurricular_opportunities : float
    cultural_norms : float
    peer_influence : float         

@dataclass 
class SimulationState:
    # simulation id of which these tables are associated to 
    mem_internal_factors: Dict[int, MemInternalFactor]
    mem_external_factors: Dict[int, MemExternalFactor]
    mem_institutional_factors: Dict[int, MemInstitutionalFactor]
