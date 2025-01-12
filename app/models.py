from datetime import datetime
from sqlalchemy import Date, UniqueConstraint
from app import db

class University(db.Model):
    __tablename__ = 'universities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = {'extend_existing': True}

    # relationships
    students = db.relationship('Student', backref='university', lazy=True)
    departments = db.relationship('Department', backref='university', lazy=True)
    institutional_factors = db.relationship('InstitutionalFactors', back_populates='university', cascade='all, delete-orphan')

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id', name='fk_department_university'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    courses = db.relationship('Course', backref='department', lazy=True)
    students = db.relationship('Student', backref='department', lazy=True)
    __table_args__ = {'extend_existing': True}

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credit_unit = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', name='fk_course_department'), nullable=False)

    student_courses = db.relationship('StudentCourse', backref='course', lazy=True)
    __table_args__ = {'extend_existing': True}

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    level = db.Column(db.Integer, nullable=False, default=100)
    gpa = db.Column(db.Float, nullable=True)

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', name='fk_student_department'), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id', name='fk_student_university'), nullable=False)

    test_results = db.relationship('TestResult', backref='related_student', lazy=True)
    enrolled_courses = db.relationship('StudentCourse', backref='student', lazy=True)
    internal_factors = db.relationship('InternalFactors', back_populates='student', uselist=False, cascade='all, delete-orphan')
    external_factors = db.relationship('ExternalFactors', back_populates='student', uselist=False, cascade='all, delete-orphan')
    institutional_factors = db.relationship('InstitutionalFactors', back_populates='student', cascade='all, delete-orphan')

    def __iter__(self):
        for attr, value in self.__dict__.items():
            if not attr.startswith("_"):
                yield attr, value



    __table_args__ = {'extend_existing': True}

class StudentCourse(db.Model):
    __tablename__ = 'student_courses'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', name='fk_student_course_student'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', name='fk_student_course_course'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='uq_student_course'),
        {'extend_existing': True}
    )

class InternalFactors(db.Model):
    __tablename__ = 'internal_factors'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', name='fk_internal_factors_student'), nullable=False)
    goal_setting = db.Column(db.Float)
    personal_ambition = db.Column(db.Float)
    interest_subject = db.Column(db.Float)
    scheduling = db.Column(db.Float)
    prioritization = db.Column(db.Float)
    consistency = db.Column(db.Float)
    study_techniques = db.Column(db.Float)
    focus_study = db.Column(db.Float)
    self_assessment = db.Column(db.Float)

    student = db.relationship('Student', back_populates='internal_factors', single_parent=True)

    __table_args__ = (
        UniqueConstraint('student_id', name='uq_internal_factors_student_id'),
        {'extend_existing': True}
    )

class ExternalFactors(db.Model):
    __tablename__ = 'external_factors'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', name='fk_external_factors_student'), nullable=False)
    family_expectations = db.Column(db.Float)
    financial_stability = db.Column(db.Float)
    access_to_resources = db.Column(db.Float)
    family_support = db.Column(db.Float)
    textbooks_availability = db.Column(db.Float)
    internet_access = db.Column(db.Float)
    lab_materials = db.Column(db.Float)
    curriculum_relevance = db.Column(db.Float)
    teaching_quality = db.Column(db.Float)
    feedback_assessment = db.Column(db.Float)

    student = db.relationship('Student', back_populates='external_factors', single_parent=True)

    __table_args__ = (
        UniqueConstraint('student_id', name='uq_external_factors_student_id'),
        {'extend_existing': True}
    )
    

class InstitutionalFactors(db.Model):
    __tablename__ = 'institutional_factors'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', name='fk_institutional_factors_student'), nullable=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id', name='fk_institutional_factors_university'), nullable=False)
    class_size = db.Column(db.Float)
    facility_availability = db.Column(db.Float)
    peer_support = db.Column(db.Float)
    academic_guidance = db.Column(db.Float)
    financial_aid = db.Column(db.Float)
    extracurricular_opportunities = db.Column(db.Float)
    cultural_norms = db.Column(db.Float)
    peer_influence = db.Column(db.Float)

    student = db.relationship('Student', back_populates='institutional_factors')
    university = db.relationship('University', back_populates='institutional_factors')

    __table_args__ = {'extend_existing': True}

class TestResult(db.Model):
    __tablename__ = 'test_results'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', name='fk_test_result_student'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    test_type = db.Column(db.String(50), nullable=True)

    __table_args__ = {'extend_existing': True}
