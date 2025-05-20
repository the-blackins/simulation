import random
from datetime import datetime, timedelta
from random import uniform

from app.models import ExternalFactors, InternalFactors


# generator functions 
def generate_phone_number():
    prefixes = ["080", "081", "090", "070"]
    prefix = random.choice(prefixes)
    
    # Generate the remaining 8 digits randomly
    remaining_digits = ''.join(str(random.randint(0, 9)) for _ in range(8))
    
    phone_number = prefix + remaining_digits
    return phone_number


def generate_dob(min_age=17, max_age=25):
    """Generate a random date of birth for a student within a given age range."""
    today = datetime.today()
    
    # Generate a random age within the specified range
    age = random.randint(min_age, max_age)
    
    # Calculate the earliest and latest possible birthdates for this age
    start_date = today.replace(year=today.year - age - 1) + timedelta(days=1)
    end_date = today.replace(year=today.year - age)
    
    # Generate a random date between start_date and end_date
    random_date = start_date + (end_date - start_date) * random.random()
    
    # Return as a Python date object instead of string
    return random_date.date()  # Convert datetime to date object


def generate_matriculation_number(university_name, department_name, year, count):
    """Generate a unique registration number for a student"""
    uni_code = ''.join(word[0] for word in university_name.split())
    dept_code = ''.join(word[0] for word in department_name.split())
    return f"{uni_code}/{dept_code}/{year}/{count:04d}"

def generate_internal_factors(student):
    """Generate realistic internal factors for a student"""
    student.internal_factors = InternalFactors(
        
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
    
    return internal_factors

def generate_external_factors(student):
    """Generate realistic external factors for a student"""
    student.external_factors = ExternalFactors(
        
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
    return external_factors