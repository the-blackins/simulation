

from datetime import datetime

def create_simulations(selected_universities):
    from app.models import Simulation
    from app import db
    simulations = []
    for university_id in selected_universities:
        simulation = Simulation(
            university_id=university_id,
            start_time=datetime.now(),
            status="Pending"  # Initial status
        )
        simulations.append(simulation)
        db.session.add(simulation)

    db.session.commit()  # Save all simulations to the database
    return simulations