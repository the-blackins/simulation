import random
from datetime import datetime, timedelta
from random import uniform
from log.logger import logger

from app.models import ExternalFactors, InternalFactors


# generator functions 
def generate_phone_number():
    prefixes = ["080", "081", "090", "070"]
    prefix = random.choice(prefixes)
    # logger.debug(f"Selected phone prefix: {prefix}")

    # Generate the remaining 8 digits randomly
    remaining_digits = ''.join(str(random.randint(0, 9)) for _ in range(8))
    phone_number = prefix + remaining_digits
    # logger.info(f"Generated phone number: {phone_number}")
    return phone_number


def generate_dob(min_age=17, max_age=25):
    """Generate a random date of birth for a student within a given age range."""
    today = datetime.today()
    # logger.debug(f"Generating DOB with min_age={min_age}, max_age={max_age}")

    # Generate a random age within the specified range
    age = random.randint(min_age, max_age)
    # logger.debug(f"Randomly selected age: {age}")

    # Calculate the earliest and latest possible birthdates for this age
    start_date = today.replace(year=today.year - age - 1) + timedelta(days=1)
    end_date = today.replace(year=today.year - age)

    # Generate a random date between start_date and end_date
    random_date = start_date + (end_date - start_date) * random.random()
    # logger.info(f"Generated date of birth: {random_date.date()}")
    
    # Return as a Python date object instead of string
    return random_date.date()  # Convert datetime to date object


def generate_matriculation_number(university_name, department_name, year, count):
    """Generate a unique registration number for a student"""
    uni_code = ''.join(word[0] for word in university_name.split())
    dept_code = ''.join(word[0] for word in department_name.split())
    matric_number = f"{uni_code}/{dept_code}/{year}/{count:04d}"
    # logger.info(f"Generated matriculation number: {matric_number}")
    return matric_number


def generate_internal_factors(student, simulation):
    """Generate realistic internal factors for a student"""
    logger.debug(f"Generating internal factors for student id: {getattr(student, 'id', 'unknown')}, simulation id: {simulation.id}")
    student.internal_factors = InternalFactors(
        simulation_id=simulation.id,
        goal_setting=uniform(5.0, 10.0),
        personal_ambition=uniform(5.0, 10.0),
        interest_subject=uniform(5.0, 10.0),
        scheduling=uniform(4.0, 9.0),
        prioritization=uniform(4.0, 9.0),
        consistency=uniform(4.0, 9.0),
        study_techniques=uniform(4.0, 9.0),
        focus_study=uniform(4.0, 9.0),
        self_assessment=uniform(4.0, 9.0)
    )
    internal_factors = student.internal_factors
    # logger.info(f"Internal factors generated: {internal_factors}")
    return internal_factors


def generate_external_factors(student, simulation):
    """Generate realistic external factors for a student"""
    logger.debug(f"Generating external factors for student id: {getattr(student, 'id', 'unknown')}, simulation id: {simulation.id}")
    student.external_factors = ExternalFactors(
        simulation_id=simulation.id,
        financial_stability=uniform(4.0, 9.0),
        access_to_resources=uniform(4.0, 9.0),
        family_support=uniform(5.0, 10.0),
        textbooks_availability=uniform(4.0, 9.0),
        internet_access=uniform(4.0, 9.0),
        lab_materials=uniform(4.0, 9.0),
        curriculum_relevance=uniform(5.0, 9.0),
        teaching_quality=uniform(5.0, 9.0),
        feedback_assessment=uniform(4.0, 9.0),
        family_expectations=uniform(5.0, 10.0)
    )
    external_factors = student.external_factors
    # logger.info(f"External factors generated: {external_factors}")
    return external_factors
