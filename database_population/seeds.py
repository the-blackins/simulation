from datetime import datetime
from random import choice, uniform
import random
from sqlite3 import IntegrityError
from app import db
from app.constants import Sex
from app.utils import random_from_enum, random_from_list
from database_population.data_generation import (generate_dob, generate_external_factors,
                                      generate_internal_factors,
                                      generate_phone_number)
from database_population.json_loader import (load_department_course_data,
                                  load_student_data, load_university_data)


from app.services.loader import load_initial_data
from app.services.memory_state import state_wrapper



def seed_simulation(universities):
    from app.models import Simulation, InstitutionalFactors, University
    
    try:
        def random_walk(base_value, step_size=0.5):
            """Generate a new value using random walk."""
            step = random.uniform(-step_size, step_size)
            new_value = base_value + step
            # Ensure the value stays within a realistic range (e.g., 0 to 10)
            return max(0, min(10, new_value))
        # 8.25975689626778  8.25975689626778
        simulations= []
        
        for university in universities:
            with db.session.no_autoflush:
                simulation = Simulation( 
                    university_id = university.id, 
                    start_time = datetime.now(),
                    status= "inactive"
                )


                simulation.institutional_factors = InstitutionalFactors( 
                    class_size=university.class_size,
                    facility_availability= university.facility_availability,
                    peer_support= university.peer_support,
                    academic_guidance= university.academic_guidance,
                    financial_aid= university.financial_aid,
                    extracurricular_opportunities= university.extracurricular_opportunities,
                    cultural_norms= university.cultural_norms,
                    peer_influence= university.peer_influence

                )
                simulations.append(simulation)
                
        db.session.add_all(simulations)                  
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Error creating simulation: {str(e)}")
        raise 
        
    
def seed_universities_and_factors(selected_universities):
    from app.models import Department, InstitutionalFactors, University
    """Seed universities and their institutional uni from JSON data"""
    try:
        # Clear existing data
        print("Clearing existing data...")
       

        universities_data = load_university_data()
        if not universities_data:
            print("No university data to seed.")
            return [], {}

        universities = []
        departments_map = {}
        DEPARTMENT_COURSES = load_department_course_data()

        for uni_data in universities_data['universities']:
            if uni_data['name'] in selected_universities:
                university = University(
                    name=uni_data['name'],
                    location=uni_data['location'],

                # Create institutional uni
                    class_size=uni_data['class_size'],
                    facility_availability=uni_data['facility_availability'],
                    peer_support=uni_data['peer_support'],
                    academic_guidance=uni_data['academic_guidance'],
                    financial_aid=uni_data['financial_aid'],
                    extracurricular_opportunities=uni_data['extracurricular_opportunities'],
                    cultural_norms=uni_data['cultural_norms'],
                    peer_influence=uni_data['peer_influence']
                )
                

                db.session.add(university)
                db.session.flush()  # Get university.id
                # Create departments for this specific university
                uni_departments = []
                for dept_name in DEPARTMENT_COURSES.keys():
                    # Make department name unique by including university name
                    unique_dept_name = f"{dept_name} - {university.name}"
                    department = Department(
                        name=unique_dept_name,
                        university_id=university.id
                    )
                    db.session.add(department)
                    uni_departments.append(department)

                departments_map[university.id] = uni_departments
                universities.append(university)
               

        db.session.commit()

            

        # Debug information
        print(f"Created {len(universities)} universities")
        for uni in universities:
            dept_count = len(departments_map.get(uni.id, []))
            print(f"University {uni.name} (ID: {uni.id}) has {dept_count} departments")

        return universities, departments_map

    except Exception as e:
        db.session.rollback()
        print(f"Error seeding universities and uni: {str(e)}")
        raise  # Re-raise the exception for debugging


def seed_courses(departments_map):
    from app.models import Course

    """
    Seed courses for each department and create a mapping of department_id to courses
    """
    try:
        courses_map = {}
        all_courses = []
        department_courses = load_department_course_data()

        # # Clear existing courses
        # db.session.query(Course).delete()
        # db.session.commit()

        for uni_departments in departments_map.values():
            for department in uni_departments:
                # Extract original department name (remove university suffix)
                original_dept_name = department.name.split(' - ')[0]
                
                if original_dept_name not in department_courses:
                    print(f"No courses found for department: {original_dept_name}")
                    continue

                dept_courses = []
                for course_data in department_courses[original_dept_name]:
                    course = Course(
                        code=f"{course_data['course_code']}_{department.id}",
                        name=course_data['course_name'],
                        credit_unit=course_data['credits'],
                        department_id=department.id
                    )
                    dept_courses.append(course)
                    all_courses.append(course)
                
                courses_map[department.id] = dept_courses

        if all_courses:
            db.session.bulk_save_objects(all_courses)
            db.session.commit()
            
            print(f"Successfully seeded {len(all_courses)} courses across {len(courses_map)} departments")
            for dept_id, courses in courses_map.items():
                print(f"Department ID {dept_id}: {len(courses)} courses")

        return courses_map

    except Exception as e:
        db.session.rollback()
        print(f"Error during course seeding: {str(e)}")
        raise

def seed_student(universities, courses_map, departments_map, num_of_students):
    from app.models import InstitutionalFactors, Student, StudentCourse, University, Simulation
    """
    populate students and distribute them across universities
    """
    try:
        student_count_map = {}
        
        
        # Get institutional uni for weighting
        university_weights = {}
        print(f"Number of universities: {len(universities)}")
        print(f"Number of departments mapped: {len(departments_map)}")
        print(f"Number of courses mapped: {len(courses_map)}")

        
        if not universities or not departments_map:
            print("No universities or departments available, cannot seed students.")
            
    
        # Calculate university weights
        for uni in universities:
            with db.session.no_autoflush:
                sim = db.session.query(Simulation).filter_by(university_id=uni.id).first()
                factors = sim.institutional_factors

            
            weight = [
                factors.facility_availability, factors.academic_guidance,
                factors.class_size, factors.peer_support,
                factors.financial_aid, factors.extracurricular_opportunities,
                factors.cultural_norms, factors.peer_influence
            ]
            university_weights[uni.id] = sum(weight) / len(weight)

        # Load student data from JSON file
        students_names = load_student_data()
        last_names = students_names["last_names"]
        male_first_names = students_names["male_first_names"]
        female_first_names = students_names["female_first_names"]

        with db.session.no_autoflush:
            simulations = {
                uni.id: Simulation.query.filter_by(university_id=uni.id).first()
                for uni in universities
            }

        try:
            student_arr = []
            internal_factor_arr = []
            external_factor_arr = []
            courses_enrolled_arr = []
            

            for _ in range(num_of_students):

                selected_uni = max(universities, key=lambda u: university_weights.get(u.id, 0) * uniform(0.8, 1.2))
                sex = random_from_enum(Sex)
                last_name = random_from_list(last_names)
                first_name = random_from_list(male_first_names if sex == Sex.M else female_first_names)
                name = f'{first_name} {last_name}'
                
                dob = generate_dob()
                phone_number = generate_phone_number()
                university = selected_uni

                available_departments = departments_map.get(university.id, [])
                if not available_departments:
                    print(f"No departments available for university {university.name} (ID: {university.id})")
                    continue
                
                department = choice(available_departments)
                dept_key = (university.id, department.id)
                student_count_map[dept_key] = student_count_map.get(dept_key, 0) + 1
                
                simulation = simulations[selected_uni.id]
                student = Student(
                    name=name,
                    simulation_id = simulation.id, 
                    phone_number=phone_number,
                    date_of_birth=dob,
                    gender=sex.value,
                    university_id=university.id,
                    department_id=department.id,
                    level=100,
                    gpa=None
                )
                student_arr.append(student)


                # db.session.flush()  # This will assign an ID to the student
                
                # Create related records
                external_factors = generate_external_factors(student, simulation)
                external_factor_arr.append(external_factors)
                
                internal_factors = generate_internal_factors(student, simulation)
                internal_factor_arr.append(internal_factors)
                # db.session.add(internal_factors)


                # db.session.add(external_factors)            
                
                available_courses = courses_map.get(department.id, [])
                if not available_courses:
                    print(f"No courses available for department {department.name} (ID: {department.id})")
                    continue
                    
                for course in available_courses:
                    enrollment = StudentCourse(
                        student_id=student.id,
                        course_id=course.id
                    )
            
                    # db.session.add(enrollment)
                    courses_enrolled_arr.append(enrollment)


            db.session.add_all(student_arr)
            
            db.session.add_all(internal_factor_arr)
            db.session.add_all(external_factor_arr)
            # db.session.add_all(courses_enrolled_arr)
            db.session.commit()


        
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error while creating student: {str(e)}")
            retry_count += 1
    
        return student_arr

    except Exception as e:
        print(f"error processing students: {str(e)}")

        
        

def loader():
    """loads data from the database"""
    mem_loader = load_initial_data()
    return mem_loader

def memory_state_population(simulation_data):
    """ initializes the memory state by loading data gotten from the database"""
    state_wrapper(simulation_data)
    

        

        
      


def seed_data(selected_universities, num_students):
    try: 
        # Clear existing data
        # ...
        db.drop_all()
        db.create_all()
        
        # Seed universities and departments
        print("Seeding selected universities and departments...")
        universities, departments_map = seed_universities_and_factors(selected_universities)

        print("creating simulation...")
        seed_simulation(universities)
        # Seed courses
        print("Seeding courses...")
        courses_map = seed_courses(departments_map)

        
        # Seed students with their uni and course enrollments
        print(f"Seeding {num_students} students with their uni and course enrollments...")
        seed_student(universities, courses_map, departments_map, num_students)

        # initiate  in-memory model
        print("creating memory...")
        
        mem_population = loader()
        print("Populating memory...")

        memory_state_population(mem_population)
        print(" Memory initialized and populated successfully ")

    except Exception as e:
        raise RuntimeError(f" Error populating database: {str(e)}")
def main():
    from app import create_app
    app = create_app()
    
    """Main function to run all seeders"""
    
    # Clear existing data
    with app.app_context():
        # Populate in order of dependencies
        print("Starting database seeding...")
        print("Clearing existing data...")

        seed_data()
        print("Database population completed")
    

if __name__ == '__main__':
    main()