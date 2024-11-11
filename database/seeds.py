from database.setup import db 
from app.models  import (
    Student, University, InstitutionalFactors, Department, Course, 
    StudentCourse, InternalFactors, ExternalFactors
)
from app.utils import(
    random_from_enum,
    random_from_list
)
import json
from random import uniform, random, choice
from datetime import datetime, timedelta  
from app.constants import Sex
from app import create_app


# load data from json files 
def load_university_data():
    try:
        with open('data/university.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading university data: {str(e)}")
        return []


def load_department_course_data():
    try:
        with open('data/department_course_data.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading department/course data: {str(e)}")
        return {}


def load_student_data():
    try:
        with open('data/students_name.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading student data: {str(e)}")
        return {"last_names": [], "male_first_names": [], "female_first_names": []}

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
    return random_date.strftime("%Y-%m-%d")

def generate_matriculation_number(university_name, department_name, year, count):
    """Generate a unique registration number for a student"""
    uni_code = ''.join(word[0] for word in university_name.split())
    dept_code = ''.join(word[0] for word in department_name.split())
    return f"{uni_code}/{dept_code}/{year}/{count:04d}"

def generate_internal_factors(student_id):
    """Generate realistic internal factors for a student"""
    return InternalFactors(
        student_id=student_id,
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
def generate_external_factors(student_id):
    """Generate realistic external factors for a student"""
    return ExternalFactors(
        student_id=student_id,
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


def seed_universities_and_factors():
    """Seed universities and their institutional factors from JSON data"""
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.session.query(InstitutionalFactors).delete()
        db.session.query(University).delete()
        db.session.commit()

        universities_data = load_university_data()
        if not universities_data:
            print("No university data to seed.")
            return [], {}

        universities = []
        departments_map = {}

        for uni_data in universities_data:
            university = University(
                name=uni_data.get('name'),
                location=uni_data.get('location')
            )
            db.session.add(university)
            db.session.flush()

        factor = InstitutionalFactors(
                university_id=university.id,
                class_size_rating=uni_data['class_size'],
                facility_rating=uni_data['facility_availability'],
                peer_support_rating=uni_data['peer_support'],
                academic_guidance_rating=uni_data['academic_guidance'],
                financial_aid_rating=uni_data['financial_aid'],
                extracurricular_rating=uni_data['extracurricular_opportunities'],
                cultural_norms_rating=uni_data['cultural_norms'],
                peer_influence_rating=uni_data['peer_influence']
            )
        db.session.add(factor) 

        DEPARTMENT_COURSES  = load_department_course_data()
        uni_departments = []

        for dept_name in DEPARTMENT_COURSES.keys():
            department = Department(
                name = dept_name, 
                university_id = university.id
            )
            db.session.add(department)
            uni_departments.append(department)

        departments_map[university.id] = uni_departments
        universities.append(university)
        # institutional_factors.append(factor)

        db.session.commit()
        return universities, departments_map

    except Exception as e:
        db.session.rollback()
        print(f"Error seeding universities and factors: {str(e)}")
        return [], {}

def seed_courses(departments_map):
    courses_map = {}  # To store course references
    all_courses = []  # List for batch insertion
    department_courses = load_department_course_data()

    # Pre-calculate all courses to insert
    for uni_departments in departments_map.values():
        for department in uni_departments:
            if department.name not in department_courses:
                print(f"No courses found for department: {department.name}")
                continue

            dept_courses = []
            for course_data in department_courses[department.name]:
                if len(course_data) != 3:
                    print(f"Invalid course data for {department.name}: {course_data}")
                    continue

                course_code, course_name, credits = course_data
                course = Course(
                    code=f"{course_code}_{department.id}",
                    name=course_name,
                    credit_unit=credits,
                    department_id=department.id
                )
                dept_courses.append(course)
                all_courses.append(course)
            courses_map[department.id] = dept_courses

    # Batch insert all courses
    try:
        # Use bulk_save_objects for better performance
        db.session.bulk_save_objects(all_courses)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error during course seeding: {str(e)}")
        raise
    
    return courses_map

    

def seed_student(universities, courses_map, departments_map,  num_of_students=5):
    """
    Seed students and distribute them across universities,
    taking into account university characteristics
    """
    current_year = datetime.now().year
    student_count_map = {}
     # Get institutional factors for weighting
    university_weights = {}

    for uni in universities:
        factors = db.session.query(InstitutionalFactors).filter_by(university_id=uni.id).first()
        if not factors:
            print(f"No factors found for university {uni.name}")
            continue
        # Calculate a basic weight based on facilities and academic guidance
        weight = [factors.facility_rating , factors.academic_guidance_rating ,
                  factors.class_size_rating , factors.peer_support_rating ,
                  factors.financial_aid_rating, factors.extracurricular_rating,
                  factors.cultural_norms_rating, factors.peer_influence_rating] 
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
            email = f'{first_name}{last_name}@gmail.com'.lower()
            dob = generate_dob()
            phone_number = generate_phone_number()

            university = selected_uni
            department = choice(departments_map.get(university.id, []))
            if not department:
                print(f"No department found for university: {university.name}")
                continue

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
            db.session.add(student)
            db.session.flush()

            internal_factors = generate_internal_factors(student.id)
            external_factors = generate_external_factors(student.id)
            db.session.add(internal_factors)
            db.session.add(external_factors)

            for course in courses_map.get(department.id, []):
                enrollment = StudentCourse(student_id=student.id, course_id=course.id)
                db.session.add(enrollment)

            if _ % 100 == 0:
                db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"Error seeding student {_}: {str(e)}")

    db.session.commit()

def main():
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
        print("Seeding universities and departments...")
        universities, departments_map = seed_universities_and_factors()
        
        print("Seeding courses...")
        courses_map = seed_courses(departments_map)
        
        print("Seeding students with their factors and course enrollments...")
        seed_student(universities, departments_map, courses_map)
        
        print("Database seeding completed!")

if __name__ == '__main__':
    main()