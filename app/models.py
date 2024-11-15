from database.setup import db
from sqlalchemy import Date
from datetime import datetime


class Simulation(db.Model):
    __tablename__ = 'simulations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num_students = db.Column(db.Integer, nullable=False)
    num_simulations = db.Column(db.Integer, nullable=False)
    final_level = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')  # Default status is 'pending'
    universities = db.Column(db.String(50), default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Automatically set when created

    def __init__(self, num_students, num_simulations, final_level, status='pending'):
        self.num_students = num_students
        self.num_simulations = num_simulations
        self.final_level = final_level
        self.status = status 
        self.created_at = datetime.utcnow()  # Set the creation time explicitly if needed

    def __repr__(self):
        return f"<Simulation(id={self.id}, num_students={self.num_students}, num_simulations={self.num_simulations}, final_level = {self.final_level}, status={self.status}, created_at={self.created_at})>"
    
    
class University(db.Model):
    __tablename__ = 'universities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

    # relationships
    students = db.relationship('Student', backref = 'university', lazy = True)
    departments = db.relationship('Department', backref='university', lazy=True)
    institutional_factor = db.relationship('InstitutionalFactors', backref='university', uselist=False)


# class Faculty(db.Model):
#     __tablename__ = 'faculties'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), unique=True, nullable=False)
#     university_id = db.Column(db.Integer, db.ForeignKey('universities.id'))
    
#     university = db.relationship('University', backref='faculties')

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
   
    courses = db.relationship('Course', backref='department', lazy=True)
    students = db.relationship('Student', backref='department', lazy= True)


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credit_unit = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    # Relationships
    student_courses = db.relationship('StudentCourse', backref='course', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    matric_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    level = db.Column(db.Integer, nullable=False, default = 100)
    gpa = db.Column(db.Float, nullable=True)
    
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    enrolled_courses = db.relationship('StudentCourse', backref='student', lazy=True)

    # Define these relationships after the factor classes
    internal_factors = db.relationship('InternalFactors', 
                                     backref=db.backref('student', uselist=False),
                                     uselist=False)
    external_factors = db.relationship('ExternalFactors', 
                                     backref=db.backref('student', uselist=False),
                                     uselist=False)
    institutional_factors = db.relationship('InstitutionalFactors', 
                                          backref=db.backref('student', uselist=False),
                                          uselist=False)


class StudentCourse(db.Model):
    __tablename__ = 'student_courses'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
   
#    timestamp 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InternalFactors(db.Model):
    __tablename__ = 'internal_factors'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    goal_setting = db.Column(db.Float)
    personal_ambition = db.Column(db.Float)
    interest_subject = db.Column(db.Float)
    scheduling = db.Column(db.Float)
    prioritization = db.Column(db.Float)
    consistency = db.Column(db.Float)
    study_techniques = db.Column(db.Float)
    focus_study = db.Column(db.Float)
    self_assessment = db.Column(db.Float)
    
    # student = db.relationship('Student', backref='internal_factors')


class ExternalFactors(db.Model):
    __tablename__ = 'external_factors'
    
    family_expectations = db.Column(db.Float)
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    financial_stability = db.Column(db.Float)
    access_to_resources = db.Column(db.Float)
    family_support = db.Column(db.Float)
    textbooks_availability = db.Column(db.Float)
    internet_access = db.Column(db.Float)
    lab_materials = db.Column(db.Float)
    curriculum_relevance = db.Column(db.Float)
    teaching_quality = db.Column(db.Float)
    feedback_assessment = db.Column(db.Float)
    
    # student = db.relationship('Student', backref='external_factors')


class InstitutionalFactors(db.Model):
    __tablename__ = 'institutional_factors'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    class_size = db.Column(db.Float)
    facility_availability = db.Column(db.Float)
    peer_support = db.Column(db.Float)
    academic_guidance = db.Column(db.Float)
    financial_aid = db.Column(db.Float)
    extracurricular_opportunities = db.Column(db.Float)
    cultural_norms = db.Column(db.Float)
    peer_influence = db.Column(db.Float)

    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    # student = db.relationship('Student', backref='institutional_factors')


