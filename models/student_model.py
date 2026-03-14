import os
from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB Connection URI provided by you
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://manojkumarprush005:manoj%40666@portfolioapi.oqztukp.mongodb.net/?appName=portfolioAPI")

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    # Using the same database name as in the seed script
    return _client['student_records']

def get_all_students_with_marks():
    """
    Fetches all students and joins them with their corresponding marks.
    Returns a list of student dictionaries containing their nested marks data.
    """
    db = get_db()
    
    # Using aggregation to join the 'students' collection with the 'marks' collection
    pipeline = [
        {
            "$lookup": {
                "from": "marks",           # Target collection to join
                "localField": "_id",       # Field from the students collection
                "foreignField": "studentId", # Field from the marks collection
                "as": "marks_data"         # Output array field
            }
        }
    ]
    
    students = list(db.students.aggregate(pipeline))
    
    # Convert MongoDB ObjectIds to strings to make them JSON serializable
    for student in students:
        student['_id'] = str(student['_id'])
        if 'marks_data' in student:
            for mark in student['marks_data']:
                mark['_id'] = str(mark['_id'])
                mark['studentId'] = str(mark['studentId'])
                
    return students

def get_student_by_id(student_id):
    """
    Fetches a single student by their ObjectId and includes their marks.
    """
    db = get_db()
    
    try:
        obj_id = ObjectId(student_id)
    except Exception:
        return None # Invalid ObjectId format
        
    pipeline = [
        {
            "$match": {
                "_id": obj_id
            }
        },
        {
            "$lookup": {
                "from": "marks",
                "localField": "_id",
                "foreignField": "studentId",
                "as": "marks_data"
            }
        }
    ]
    
    result = list(db.students.aggregate(pipeline))
    if result:
        student = result[0]
        student['_id'] = str(student['_id'])
        if 'marks_data' in student:
            for mark in student['marks_data']:
                mark['_id'] = str(mark['_id'])
                mark['studentId'] = str(mark['studentId'])
        return student
    return None

def get_student_by_email(email):
    """
    Fetches a single student by their email address and includes their marks.
    """
    db = get_db()
    
    pipeline = [
        {
            "$match": {
                "email": email
            }
        },
        {
            "$lookup": {
                "from": "marks",
                "localField": "_id",
                "foreignField": "studentId",
                "as": "marks_data"
            }
        }
    ]
    
    result = list(db.students.aggregate(pipeline))
    if result:
        student = result[0]
        student['_id'] = str(student['_id'])
        if 'marks_data' in student:
            for mark in student['marks_data']:
                mark['_id'] = str(mark['_id'])
                mark['studentId'] = str(mark['studentId'])
        return student
    return None
