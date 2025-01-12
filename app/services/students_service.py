from app.models import Student, TestResult, InternalFactors, ExternalFactors, InstitutionalFactors
from statistics import mean 
import json



def test_simulation_performance(student_id):
    from app import db 
    student = Student.query.get(student_id)
  
