"""Queries and loads data from the database"""

from sqlalchemy.orm import joinedload
from collections import defaultdict


def load_initial_data():
    try:
        from app.models import  InstitutionalFactors, Student, Simulation, InternalFactors, ExternalFactors
        from app import db
        simulations = Simulation.query.all()
        # grouped_list = defaultdict(list)
        loaded_data = []

        for simulation in simulations:

            loaded_internal_factors = (db.session.query(InternalFactors).
            join(InternalFactors.students).
            join(Student.simulation).
            filter(Simulation.id == simulation.id).
            all())

            loaded_external_factors = (db.session.query(ExternalFactors).
            join(ExternalFactors.students).
            join(Student.simulation).
            filter(Simulation.id == simulation.id).
            all())

            loaded_institional_factors = (db.session.query(InstitutionalFactors).
            join(InstitutionalFactors.simulation).
            filter(Simulation.id == simulation.id).
            all()
            )

            dict_list = {
                "simulation_id": simulation.id,
                "internal_factors": loaded_internal_factors,
                "external_factors": loaded_external_factors,
                "institutional_factors": loaded_institional_factors,
            }
            loaded_data.append(dict_list)

        
    
        return loaded_data

    except Exception as e:
        raise RuntimeError(f'error loading data from the database: {str(e)}') 
    

    