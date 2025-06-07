import json
from log.logger import logger

# load data from json files 
def load_university_data():
    try:
        with open('data/university.json', 'r') as file:
            data = json.load(file)
            logger.info("Successfully loaded university data")
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Error loading university data: %s", str(e))
        return []


def load_department_course_data():
    try:
        with open('data/department_course_data.json', 'r') as file:
            data = json.load(file)
            logger.info("Successfully loaded department/course data")
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Error loading department/course data: %s", str(e))
        return {}


def load_student_data():
    try:
        with open('data/students_name.json', 'r') as file:
            data = json.load(file)
            logger.info("Successfully loaded student data")
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Error loading student data: %s", str(e))
        return {"last_names": [], "male_first_names": [], "female_first_names": []}
