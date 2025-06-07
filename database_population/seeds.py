from datetime import datetime
from random import choice, uniform
import random
from sqlite3 import IntegrityError
from app import db
from app.constants import Sex
from app.utils import random_from_enum, random_from_list
from database_population.data_generation import (
    generate_dob, generate_external_factors,
    generate_internal_factors, generate_phone_number
)
from database_population.json_loader import (
    load_department_course_data,
    load_student_data, load_university_data
)
from log.logger import logger


def seed_simulation(universities):
    from app.models import Simulation, InstitutionalFactors

    try:

        simulations = []
        logger.info("Starting simulation seeding...")

        for university in universities:
            with db.session.no_autoflush:
                simulation = Simulation(
                    university_id=university.id,
                    start_time=datetime.now(),
                    status="inactive"
                )

                simulation.institutional_factors = InstitutionalFactors(
                    class_size=university.class_size,
                    facility_availability=university.facility_availability,
                    peer_support=university.peer_support,
                    academic_guidance=university.academic_guidance,
                    financial_aid=university.financial_aid,
                    extracurricular_opportunities=university.extracurricular_opportunities,
                    cultural_norms=university.cultural_norms,
                    peer_influence=university.peer_influence
                )
                simulations.append(simulation)

        db.session.add_all(simulations)
        db.session.commit()
        logger.info(f"Seeded {len(simulations)} simulations.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating simulation: {str(e)}")
        raise


def seed_universities_and_factors(selected_universities):
    from app.models import Department, University
    try:
        logger.info("Seeding selected universities and departments...")
        universities_data = load_university_data()

        if not universities_data:
            logger.warning("No university data to seed.")
            return [], {}

        universities = []
        departments_map = {}
        DEPARTMENT_COURSES = load_department_course_data()

        for uni_data in universities_data['universities']:
            if uni_data['name'] in selected_universities:
                university = University(
                    name=uni_data['name'],
                    location=uni_data['location'],
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
                db.session.flush()

                uni_departments = []
                for dept_name in DEPARTMENT_COURSES.keys():
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
        logger.info(f"Created {len(universities)} universities.")

        for uni in universities:
            dept_count = len(departments_map.get(uni.id, []))
            logger.debug(f"University {uni.name} (ID: {uni.id}) has {dept_count} departments")

        return universities, departments_map

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding universities and departments: {str(e)}")
        raise


def seed_courses(departments_map):
    from app.models import Course
    try:
        courses_map = {}
        all_courses = []
        department_courses = load_department_course_data()

        for uni_departments in departments_map.values():
            for department in uni_departments:
                original_dept_name = department.name.split(' - ')[0]

                if original_dept_name not in department_courses:
                    logger.warning(f"No courses found for department: {original_dept_name}")
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

            # logger.info(f"Successfully seeded {len(all_courses)} courses across {len(courses_map)} departments")
            for dept_id, courses in courses_map.items():
                logger.debug(f"Department ID {dept_id}: {len(courses)} courses")

        return courses_map

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during course seeding: {str(e)}")
        raise


def seed_student(universities, courses_map, departments_map, num_of_students):
    from app.models import Student, StudentCourse, Simulation
    try:
        student_count_map = {}
        logger.info("Starting student seeding...")
        logger.debug(f"Number of universities: {len(universities)}")
        logger.debug(f"Number of departments mapped: {len(departments_map)}")
        logger.debug(f"Number of courses mapped: {len(courses_map)}")

        if not universities or not departments_map:
            logger.warning("No universities or departments available, cannot seed students.")
            return []

        university_weights = {}
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

        students_names = load_student_data()
        last_names = students_names["last_names"]
        male_first_names = students_names["male_first_names"]
        female_first_names = students_names["female_first_names"]

        with db.session.no_autoflush:
            simulations = {
                uni.id: Simulation.query.filter_by(university_id=uni.id).first()
                for uni in universities
            }

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

            available_departments = departments_map.get(selected_uni.id, [])
            if not available_departments:
                logger.warning(f"No departments available for university {selected_uni.name} (ID: {selected_uni.id})")
                continue

            department = choice(available_departments)
            dept_key = (selected_uni.id, department.id)
            student_count_map[dept_key] = student_count_map.get(dept_key, 0) + 1

            simulation = simulations[selected_uni.id]
            student = Student(
                name=name,
                simulation_id=simulation.id,
                phone_number=phone_number,
                date_of_birth=dob,
                gender=sex.value,
                university_id=selected_uni.id,
                department_id=department.id,
                level=100,
                gpa=None
            )
            student_arr.append(student)

            external_factors = generate_external_factors(student, simulation)
            external_factor_arr.append(external_factors)

            internal_factors = generate_internal_factors(student, simulation)
            internal_factor_arr.append(internal_factors)

            available_courses = courses_map.get(department.id, [])
            if not available_courses:
                logger.warning(f"No courses available for department {department.name} (ID: {department.id})")
                continue

            for course in available_courses:
                enrollment = StudentCourse(
                    student_id=student.id,
                    course_id=course.id
                )
                courses_enrolled_arr.append(enrollment)

        db.session.add_all(student_arr)
        db.session.add_all(internal_factor_arr)
        db.session.add_all(external_factor_arr)
        db.session.commit()

        logger.info(f"Seeded {len(student_arr)} students.")
        return student_arr

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing students: {str(e)}")
        raise


def seed_data(selected_universities, num_students):
    try:
        db.drop_all()
        db.create_all()
        logger.info("Database reset successful.")

        universities, departments_map = seed_universities_and_factors(selected_universities)
        seed_simulation(universities)
        courses_map = seed_courses(departments_map)
        seed_student(universities, courses_map, departments_map, num_students)

        logger.info("Data seeding complete.")
    except Exception as e:
        logger.error(f"Error during full data seed process: {str(e)}")
        raise
