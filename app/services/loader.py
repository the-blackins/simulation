"""Queries and loads data from the database"""

from sqlalchemy.orm import joinedload
from collections import defaultdict

def load_initial_data():
    from app.models import  InstitutionalFactors, Student, Simulation
    from app import db

    try:
        grouped_list = defaultdict(list)
        loaded_data = []

        loaded_institional_factor_data = (
            db.session.query(InstitutionalFactors)
            .options(joinedload(InstitutionalFactors.simulation).load_only("id"))
            .all()
        )   


        loaded_institional_factor_data = db.session.query(InstitutionalFactors).options(joinedload(InstitutionalFactors.simulation)).all()
        loaded_internal_factor_data = db.session.query(Student).options(joinedload(Student.internal_factors)).all()
        loaded_external_factor_data = db.session.query(Student).options(joinedload(Student.external_factors)).all()

        loaded_data.append(loaded_external_factor_data)
        loaded_data.append(loaded_institional_factor_data) 
        loaded_data.append(loaded_internal_factor_data)

        return loaded_data

    except Exception as e:
        raise f' error loading data: {str(e)}'
    

    