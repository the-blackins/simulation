from database.setup import db 
from app.models  import (
    Student, University, InstitutionalFactors, Department, Course, 
    StudentCourse, InternalFactors, ExternalFactors
)
from app.utils import(
    random_from_enum,
    random_from_list
)

from database.data_generation import(
    generate_phone_number, generate_dob, 
    generate_matriculation_number, generate_internal_factors,
    generate_external_factors
)
from database.json_loader import(
    load_department_course_data, load_student_data, load_university_data
)
from random import uniform, random, choice
from datetime import datetime
from app.constants import Sex

def seed_universities_and_factors(selected_universities):
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



def seed_student(universities, courses_map, departments_map,  num_of_students):
    """
    Seed students and distribute them across universities,
    taking into account university characteristics
    """
    current_year = datetime.now().year
    student_count_map = {}
     # Get institutional factors for weighting
    university_weights = {}
     # Add debug prints at the start
    print(f"Number of universities: {len(universities)}")
    print(f"Number of departments mapped: {len(departments_map)}")
    print(f"Number of courses mapped: {len(courses_map)}")

     # Check the structure of your maps
    print("Department map keys:", list(departments_map.keys()))
    print("Course map keys:", list(courses_map.keys()))
    

    
    if not universities or not departments_map:
        print("No universities or departments available, cannot seed students.")
        return
    all_students = []
    all_internal_factors = []
    all_external_factors = []
    all_enrollments = []

    for uni in universities:
        factors = db.session.query(InstitutionalFactors).filter_by(university_id=uni.id).first()
        if not factors:
            print(f"No factors found for university {uni.name}")
            continue
        # Calculate a basic weight based on facilities and academic guidance
        weight = [factors.facility_availability , factors.academic_guidance ,
                  factors.class_size , factors.peer_support ,
                  factors.financial_aid, factors.extracurricular_opportunities,
                  factors.cultural_norms, factors.peer_influence] 
        university_weights[uni.id] = sum(weight) / len(weight)

#   load student data from json file 
    students_names = load_student_data()
    
    last_names = students_names["last_names"]
    male_first_names = students_names["male_first_names"]
    female_first_names = students_names["female_first_names"]


    for _ in range(num_of_students):
        try:
            selected_uni = max(universities, key=lambda u: university_weights.get(u.id, 0) * uniform(0.8, 1.2))
            sex = random_from_enum(Sex)
            last_name = random_from_list(last_names)
            first_name = random_from_list(male_first_names if sex == Sex.M else female_first_names)
            name = f'{first_name} {last_name}'
            email = f'{first_name}.{last_name}@gmail.com'.lower()
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
            matriculation_number = generate_matriculation_number(
                university.name, department.name, current_year, student_count_map[dept_key]
            )

            student = Student(
                name=name, matric_number=matriculation_number, email=email,
                phone_number=phone_number, date_of_birth=dob, gender=sex.value,
                university_id=university.id, department_id=department.id, level = None, 
                gpa = None
            )
            all_students.append(student)


            internal_factors = generate_internal_factors(student.id)
            all_internal_factors.append(internal_factors)

            external_factors = generate_external_factors(student.id)
            all_external_factors.append(external_factors)
            
            

            available_courses = courses_map.get(department.id, [])
            if not available_courses:
                print(f"No courses available for department {department.name} (ID: {department.id})")
                continue
            for course in available_courses:
                enrollment = StudentCourse(
                    student_id=student.id,
                    course_id=course.id,
                )
                
                all_enrollments.append(enrollment)
            

            if len(all_students) % 100 == 0:
                try:
                    db.session.bulk_save_objects(all_students)
                    db.session.bulk_save_objects(all_internal_factors)
                    db.session.bulk_save_objects(all_external_factors)
                    db.session.bulk_save_objects(all_enrollments)
                    db.session.commit()
                    print(all_enrollments)
                    all_students = []
                    all_internal_factors = []
                    all_external_factors = []
                    all_enrollments = []
                except Exception as e:
                    db.session.rollback()
                    print(f"Error during student seeding: {str(e)}")
                    raise
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding student {_}: {str(e)}")
    
    if all_students:
        try:
            db.session.bulk_save_objects(all_students)
            db.session.bulk_save_objects(all_internal_factors)
            db.session.bulk_save_objects(all_external_factors)
            db.session.bulk_save_objects(all_enrollments)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error during student seeding: {str(e)}")
            raise

def seed_data(selected_universities, num_students):
    # Clear existing data
    # ...

    # Seed universities and departments
    print("Seeding selected universities and departments...")
    universities, departments_map = seed_universities_and_factors(selected_universities)

    # Seed courses
    print("Seeding courses...")
    courses_map = seed_courses(departments_map)

    # Seed students with their factors and course enrollments
    print(f"Seeding {num_students} students with their factors and course enrollments...")
    seed_student(universities, courses_map, departments_map, num_students)

    print("Database seeding completed!")
    

def main():
    from app import create_app
    app = create_app()

    """Main function to run all seeders"""
    
    # Clear existing data
    with app.app_context():
        print("Starting database seeding...")
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        db.session.query(StudentCourse).delete()
        db.session.query(InternalFactors).delete()
        db.session.query(ExternalFactors).delete()
        db.session.query(Student).delete()
        db.session.query(Course).delete()
        db.session.query(Department).delete()
        db.session.query(InstitutionalFactors).delete()
        db.session.query(University).delete()
        db.session.commit()
    
        # Seed in order of dependencies
        seed_data()

if __name__ == '__main__':
    main()