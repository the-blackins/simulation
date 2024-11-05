from database.setup import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    matric_number = db.Column(db.String(15), unique=True, nullable=False)  # unique student identifier
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=False)  # 'Male' or 'Female'
    year_of_entry = db.Column(db.Integer, nullable=False)  # entry year (e.g., 2022)
    level = db.Column(db.Integer, nullable=False)  # e.g., 100, 200, etc.
    gpa = db.Column(db.Float, nullable=True)  # optional GPA field
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)  # linked to Department


class University(db.Model):
    __tablename__ = 'universities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    students = db.relationship('Student', backref='university', lazy=True)


class Faculty(db.Model):
    __tablename__ = 'faculties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'))
    departments = db.relationship('Department', backref='faculty', lazy=True)

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'), nullable=False)
    students = db.relationship('Student', backref='department', lazy=True)
    courses = db.relationship('Course', backref='department', lazy=True)


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)  # e.g., 'CSC101'
    name = db.Column(db.String(100), nullable=False)
    credit_units = db.Column(db.Integer, nullable=False)  # e.g., 3 credit units
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    students = db.relationship('StudentCourse', backref='course', lazy=True)

class StudentCourse(db.Model):
    __tablename__ = 'student_courses'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    grade = db.Column(db.String(2), nullable=True)  
