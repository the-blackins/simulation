from datetime import datetime
from random import choice, random, uniform
from sqlite3 import IntegrityError

from app import db
from app.constants import Sex
from app.utils import random_from_enum, random_from_list
from database.data_generation import (generate_dob, generate_external_factors,
                                      generate_internal_factors,
                                      generate_phone_number)
from database.json_loader import (load_department_course_data,
                                  load_student_data, load_university_data)


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
                    class_size=uni_data['class_size'],
                    facility_availability=uni_data['facility_availability'],
                    peer_support=uni_data['peer_support'],
                    academic_guidance=uni_data['academic_guidance'],
                    financial_aid=uni_data['financial_aid'],
                    extracurricular_opportunities=uni_data['extracurricular_opportunities'],
                    cultural_norms=uni_data['cultural_norms'],
                    peer_influence=uni_data['peer_influence']
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

# def generate_unique_matriculation_number(university_name, department_name, current_year, student_count, matric_set):
#     """
#     Generate a unique matriculation number
#     Returns tuple of (matric_number, success)
#     """
#     MAX_ATTEMPTS = 5000  # Prevent infinite loops
#     attempt = 0
    
#     while attempt < MAX_ATTEMPTS:
#         matric = generate_matriculation_number(
#             university_name, 
#             department_name, 
#             current_year, 
#             student_count + attempt
#         )
#         if matric not in matric_set:
#             matric_set.add(matric)
#             return matric
#         attempt += 1
    
#     raise ValueError(f"Could not generate unique matriculation number after {MAX_ATTEMPTS} attempts")

# def seed_student(universities, courses_map, departments_map, num_of_students):
#     from app.models import InstitutionalFactors, Student, StudentCourse
#     """
#     Seed students and distribute them across universities,
#     taking into account university characteristics
#     """
#     current_year = datetime.now().year
#     student_count_map = {}
#     # email_set = set()  # Track used email addresses
#     # matric_set = set()  # Track used matriculation numbers
#     department_counters = {}
    
#     # Get institutional factors for weighting
#     university_weights = {}
#     print(f"Number of universities: {len(universities)}")
#     print(f"Number of departments mapped: {len(departments_map)}")
#     print(f"Number of courses mapped: {len(courses_map)}")
    
#     # def get_next_matric_number(university, department):
#     #     """Generate the next available matriculation number for a department"""
#     #     dept_key = (university.id, department.id)
#     #     if dept_key not in department_counters:
#     #         department_counters[dept_key] = 0
        
#     #     while True:
#     #         department_counters[dept_key] += 1
#     #         matric = generate_matriculation_number(
#     #             university.name,
#     #             department.name,
#     #             current_year,
#     #             department_counters[dept_key]
#     #         )
#     #         if matric not in matric_set:
#     #             matric_set.add(matric)
#     #             return matric
            
#     if not universities or not departments_map:
#         print("No universities or departments available, cannot seed students.")
#         return
        
#     all_students = []
#     all_internal_factors = []
#     all_external_factors = []
#     all_enrollments = []

#     # Calculate university weights
#     for uni in universities:
#         factors = db.session.query(InstitutionalFactors).filter_by(university_id=uni.id).first()
#         if not factors:
#             print(f"No factors found for university {uni.name}")
#             continue
#         weight = [
#             factors.facility_availability, factors.academic_guidance,
#             factors.class_size, factors.peer_support,
#             factors.financial_aid, factors.extracurricular_opportunities,
#             factors.cultural_norms, factors.peer_influence
#         ]
#         university_weights[uni.id] = sum(weight) / len(weight)

#     # Load student data from JSON file
#     students_names = load_student_data()
#     last_names = students_names["last_names"]
#     male_first_names = students_names["male_first_names"]
#     female_first_names = students_names["female_first_names"]

#     # def generate_unique_email(first_name, last_name, email_set):
#     #     """Generate a unique email address"""
#     #     base_email = f'{first_name}.{last_name}@gmail.com'.lower()
#     #     if base_email not in email_set:
#     #         email_set.add(base_email)
#     #         return base_email
        
#     #     counter = 1
#     #     while True:
#     #         email = f'{first_name}.{last_name}{counter}@gmail.com'.lower()
#     #         if email not in email_set:
#     #             email_set.add(email)
#     #             return email
#     #         counter += 1

#     students_processed = 0
#     max_retries = 3  # Maximum number of retries for each student

#     while students_processed < num_of_students:
#         retry_count = 0
#         while retry_count < max_retries:
#             try:
#                 selected_uni = max(universities, key=lambda u: university_weights.get(u.id, 0) * uniform(0.8, 1.2))
#                 sex = random_from_enum(Sex)
#                 last_name = random_from_list(last_names)
#                 first_name = random_from_list(male_first_names if sex == Sex.M else female_first_names)
#                 name = f'{first_name} {last_name}'
                
#                 # Generate unique email
#                 # email = generate_unique_email(first_name, last_name, email_set)
                
#                 dob = generate_dob()
#                 phone_number = generate_phone_number()
#                 university = selected_uni

#                 available_departments = departments_map.get(university.id, [])
#                 if not available_departments:
#                     print(f"No departments available for university {university.name} (ID: {university.id})")
#                     continue
                
#                 department = choice(available_departments)
#                 dept_key = (university.id, department.id)
#                 student_count_map[dept_key] = student_count_map.get(dept_key, 0) + 1
                
#                 # # Generate unique matriculation number
#                 # try:
#                 #     matriculation_number = get_next_matric_number(selected_uni, department)

#                 # except ValueError as e:
#                 #     print(f"Error generating matriculation number: {str(e)}")
#                 #     retry_count += 1
#                 #     continue

#                 student = Student(
#                     name=name,
#                     # matric_number=matriculation_number,
#                     # email=email,
#                     phone_number=phone_number,
#                     date_of_birth=dob,
#                     gender=sex.value,
#                     university_id=university.name,
#                     department_id=department.name,
#                     level=None,
#                     gpa=None
#                 )
#                 all_students.append(student)
                
#                 # Create related records
#                 internal_factors = generate_internal_factors(student.id)
#                 all_internal_factors.append(internal_factors)

#                 external_factors = generate_external_factors(student.id)
#                 all_external_factors.append(external_factors)

#                 available_courses = courses_map.get(department.id, [])
#                 if not available_courses:
#                     print(f"No courses available for department {department.name} (ID: {department.id})")
#                     continue
                    
#                 for course in available_courses:
#                     enrollment = StudentCourse(
#                         student_id=student.id,
#                         course_id=course.id
#                     )
#                     all_enrollments.append(enrollment)

#                 students_processed += 1
#                 break  # Successfully created student, exit retry loop

#             except IntegrityError as e:
#                 db.session.rollback()
#                 print(f"Integrity error while creating student: {str(e)}")
#                 retry_count += 1
#                 continue
#             except Exception as e:
#                 db.session.rollback()
#                 print(f"Unexpected error while creating student: {str(e)}")
#                 retry_count += 1
#                 continue

#         if retry_count >= max_retries:
#             print(f"Failed to create student after {max_retries} attempts, skipping...")
#             continue

#         # Commit in batches of 100
#         if len(all_students) >= 100:
#             try:
#                 db.session.bulk_save_objects(all_students)
#                 db.session.bulk_save_objects(all_internal_factors)

#                 for external_fact in all_external_factors:
#                     db.session.add(external_fact)

#                 # db.session.bulk_save_objects(all_external_factors)
#                 db.session.bulk_save_objects(all_enrollments)
#                 db.session.commit()
                
#                 all_students = []
#                 all_internal_factors = []
#                 all_external_factors = []
#                 all_enrollments = []
#             except IntegrityError as e:
#                 db.session.rollback()
#                 print(f"Integrity error during batch commit: {str(e)}")
#             except Exception as e:
#                 db.session.rollback()
#                 print(f"Error during batch commit: {str(e)}")
#                 raise

#     # Commit any remaining records
#     if all_students:
#         try:
#             db.session.bulk_save_objects(all_students)
#             db.session.bulk_save_objects(all_internal_factors)
#             db.session.bulk_save_objects(all_external_factors)
#             db.session.bulk_save_objects(all_enrollments)
#             db.session.commit()
#         except Exception as e:
#             db.session.rollback()
#             print(f"Error during final commit: {str(e)}")
#             raise

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