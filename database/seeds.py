from datetime import datetime
from random import choice, uniform
import random
from sqlite3 import IntegrityError

from app import db
from app.constants import Sex
from app.utils import random_from_enum, random_from_list
from database.data_generation import (generate_dob, generate_external_factors,
                                      generate_internal_factors,
                                      generate_phone_number)
from database.json_loader import (load_department_course_data,
                                  load_student_data, load_university_data)


def seed_simulation(selected_universities):
    from app.models import Simulation, InstitutionalFactors
    try:
    
        for university in selected_universities:
            simulation = Simulation(
                university_id = university.id, 
                start_time = datetime.now(),
                status= "Running"
            )
            db.session.add(simulation)
            db.session.commit()

        # Create factors and associate via the relationship
        factor = InstitutionalFactors()
        simulation.institutional_factors.append(factor)  # Auto-sets simulation_id
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating simulation: {str(e)}")
        raise 
        

def seed_universities_and_factors(selected_universities):
    from app.models import Department, InstitutionalFactors, University
    """Seed universities and their institutional factors from JSON data"""
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.session.query(InstitutionalFactors).delete()
        db.session.query(University).delete()
        db.session.query(Department).delete()  # Added this to ensure clean state
        db.session.commit()

        universities_data = load_university_data()
        if not universities_data:
            print("No university data to seed.")
            return [], {}

        universities = []
        departments_map = {}
        DEPARTMENT_COURSES = load_department_course_data()
        def random_walk(base_value, step_size=0.5):
            """Generate a new value using random walk."""
            step = random.uniform(-step_size, step_size)
            new_value = base_value + step
            # Ensure the value stays within a realistic range (e.g., 0 to 10)
            return max(0, min(10, new_value))


        for uni_data in universities_data['universities']:
            if uni_data['name'] in selected_universities:
                university = University(
                    name=uni_data['name'],
                    location=uni_data['location']
                )
                db.session.add(university)
                db.session.flush()  # Get university.id

                # Create institutional factors
                factor = InstitutionalFactors(
                    university_id=university.id,
                    class_size=random_walk(uni_data['class_size']),
                    facility_availability=random_walk(uni_data['facility_availability']),
                    peer_support=random_walk(uni_data['peer_support']),
                    academic_guidance=random_walk(uni_data['academic_guidance']),
                    financial_aid=random_walk(uni_data['financial_aid']),
                    extracurricular_opportunities=random_walk(uni_data['extracurricular_opportunities']),
                    cultural_norms=random_walk(uni_data['cultural_norms']),
                    peer_influence=random_walk(uni_data['peer_influence'])
                )
                db.session.add(factor)

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
        print(f"Error seeding universities and factors: {str(e)}")
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

        # Clear existing courses
        db.session.query(Course).delete()
        db.session.commit()

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
    from app.models import InstitutionalFactors, Student, StudentCourse
    """
    Seed students and distribute them across universities,
    taking into account university characteristics
    """
    current_year = datetime.now().year
    student_count_map = {}
    department_counters = {}
    
    # Get institutional factors for weighting
    university_weights = {}
    print(f"Number of universities: {len(universities)}")
    print(f"Number of departments mapped: {len(departments_map)}")
    print(f"Number of courses mapped: {len(courses_map)}")
    
    if not universities or not departments_map:
        print("No universities or departments available, cannot seed students.")
        return
        
    # Calculate university weights
    for uni in universities:
        factors = db.session.query(InstitutionalFactors).filter_by(university_id=uni.id).first()
        if not factors:
            print(f"No factors found for university {uni.name}")
            continue
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

    students_processed = 0
    max_retries = 3  # Maximum number of retries for each student

    while students_processed < num_of_students:
        retry_count = 0
        while retry_count < max_retries:
            try:
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
                
                student = Student(
                    name=name,
                    phone_number=phone_number,
                    date_of_birth=dob,
                    gender=sex.value,
                    university_id=university.id,
                    department_id=department.id,
                    level=100,
                    gpa=None
                )
                db.session.add(student)
                db.session.flush()  # This will assign an ID to the student
                
                # Create related records
                internal_factors = generate_internal_factors(student)
                db.session.add(internal_factors)

                external_factors = generate_external_factors(student)
                db.session.add(external_factors)

                available_courses = courses_map.get(department.id, [])
                if not available_courses:
                    print(f"No courses available for department {department.name} (ID: {department.id})")
                    continue
                    
                for course in available_courses:
                    enrollment = StudentCourse(
                        student_id=student.id,
                        course_id=course.id
                    )
                    db.session.add(enrollment)

                db.session.commit()
                students_processed += 1
                break  # Successfully created student, exit retry loop

            except IntegrityError as e:
                db.session.rollback()
                print(f"Integrity error while creating student: {str(e)}")
                retry_count += 1
                continue
            except Exception as e:
                db.session.rollback()
                print(f"Unexpected error while creating student: {str(e)}")
                retry_count += 1
                continue

        if retry_count >= max_retries:
            print(f"Failed to create student after {max_retries} attempts, skipping...")
            continue

    print(f"Successfully processed {students_processed} students.")

def seed_data(selected_universities, num_students):
    # Clear existing data
    # ...
    db.drop_all()
    db.create_all()
    
    # Seed universities and departments
    print("Seeding selected universities and departments...")
    universities, departments_map = seed_universities_and_factors(selected_universities)

    # Seed courses
    print("Seeding courses...")
    courses_map = seed_courses(departments_map)

    # creating simulation
    print("creating simulation...")
    seed_simulation(selected_universities)
    
    # Seed students with their factors and course enrollments
    print(f"Seeding {num_students} students with their factors and course enrollments...")
    seed_student(universities, courses_map, departments_map, num_students)

    # print("Database seeding completed!")
    

def main():
    from app import create_app
    app = create_app()
    from app.models import (Course, Department, ExternalFactors,
                            InstitutionalFactors, InternalFactors, Student,
                            StudentCourse, University)
    """Main function to run all seeders"""
    
    # Clear existing data
    with app.app_context():
        print("Starting database seeding...")
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        seed_data()
        print("Database population completed")
    
        # Seed in order of dependencies

if __name__ == '__main__':
    main()