"""Queries and loads data from the database"""

from sqlalchemy.orm import joinedload
from collections import defaultdict
from log.logger import logger  # Make sure logger is properly set up and imported


def load_initial_data():
    try:
        from app.models import InstitutionalFactors, Student, Simulation, InternalFactors, ExternalFactors
        from app import db

        logger.info("Querying simulations from the database...")
        simulations = Simulation.query.all()
        loaded_data = []

        for simulation in simulations:
            logger.info(f"Loading data for simulation ID: {simulation.id}")

            loaded_internal_factors = (
                db.session.query(InternalFactors)
                .join(InternalFactors.students)
                .join(Student.simulation)
                .filter(Simulation.id == simulation.id)
                .all()
            )
            logger.debug(f"Loaded {len(loaded_internal_factors)} internal factors for simulation {simulation.id}")

            loaded_external_factors = (
                db.session.query(ExternalFactors)
                .join(ExternalFactors.students)
                .join(Student.simulation)
                .filter(Simulation.id == simulation.id)
                .all()
            )
            logger.debug(f"Loaded {len(loaded_external_factors)} external factors for simulation {simulation.id}")

            loaded_institutional_factors = (
                db.session.query(InstitutionalFactors)
                .join(InstitutionalFactors.simulation)
                .filter(Simulation.id == simulation.id)
                .all()
            )
            logger.debug(f"Loaded {len(loaded_institutional_factors)} institutional factors for simulation {simulation.id}")

            
            dict_list = {
                "simulation_id": simulation.id,
                "internal_factors": loaded_internal_factors,
                "external_factors": loaded_external_factors,
                "institutional_factors": loaded_institutional_factors,
            }
            loaded_data.append(dict_list)
            
        logger.info(f"Finished loading data for {len(simulations)} simulations.")

        return loaded_data

    except Exception as e:
        logger.exception("Error loading data from the database.")
        raise RuntimeError(f"Error loading data from the database: {str(e)}")
