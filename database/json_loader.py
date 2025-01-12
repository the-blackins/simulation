import json


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


