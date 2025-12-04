from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field,EmailStr
from pymongo import MongoClient,errors
from bson import ObjectId
from bson.errors import InvalidId
import re
import logging

app = FastAPI()

class Student(BaseModel):
    student_id: str | None = None   # allow custom id like "1"
    name: str
    age: int
    grade: str
    email: str

class Course(BaseModel):
    course_id: str | None = None   # allow custom id like "10"
    course_name: str
    instructor: str

class Enrollment(BaseModel):
    student_id: str
    course_id: str


client = MongoClient("mongodb://localhost:27017")
db = client["school_db"]                                 #db connection

students_col = db["students"]
courses_col = db["courses"]
enrollments_col = db["enrollments"]

@app.get("/")
def home():
    return {"message": "Connected to MongoDB: school_db"}


@app.post("/students")
def add_student(student: Student):
    student_dict = student.dict()
    result = students_col.insert_one(student_dict)
    student_dict["_id"] = str(result.inserted_id)
    return student_dict

@app.get("/students")
def get_students():
    students = students_col.find()
    return [{**s, "_id": str(s["_id"])} for s in students]


@app.post("/courses")
def add_course(course: Course):
    course_dict = course.dict()
    result = courses_col.insert_one(course_dict)
    course_dict["_id"] = str(result.inserted_id)
    return course_dict

@app.get("/courses")
def get_courses():
    courses = courses_col.find()
    return [{**c, "_id": str(c["_id"])} for c in courses]


@app.post("/enrollments")
def add_enrollment(enrollment: Enrollment):
    data = enrollment.dict()
    result = enrollments_col.insert_one(data)
    return {"enrollment_id": str(result.inserted_id), **data}

@app.get("/enrollments")
def get_enrollments():
    try:
        enrollments = enrollments_col.find()
        output = []
        for e in enrollments:
            enrollment_data = {
                "enrollment_id": str(e.get("_id")),
                "student_id": e.get("student_id"),
                "course_id": e.get("course_id"),
                "student": None,
                "course": None
            }

            # lookup student
            student = students_col.find_one({"student_id": e.get("student_id")})
            if student:
                enrollment_data["student"] = {
                    "student_id": student.get("student_id"),
                    "name": student.get("name"),
                    "age": student.get("age"),
                    "grade": student.get("grade"),
                    "email": student.get("email")
                }

            # lookup course
            course = courses_col.find_one({"course_id": e.get("course_id")})
            if course:
                enrollment_data["course"] = {
                    "course_id": course.get("course_id"),
                    "course_name": course.get("course_name"),
                    "instructor": course.get("instructor")
                }

            output.append(enrollment_data)

        return output

    except Exception as e:
        return {"error": str(e)}


#2.

@app.get("/databases")
def list_databases():
    try:
        db_list = client.list_database_names()  # List all databases
        return {"databases": db_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#3.

@app.post("/studentsnew")
def add_student(student: Student):
    try:
        student_dict = student.model_dump()
        result = db.students.insert_one(student_dict)
        student_dict["student_id"] = str(result.inserted_id)
        return student_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 

@app.get("/studentsnew")
def get_studentsnew():
    students = list(db.students.find())
    for s in students:
        s["student_id"] = str(s["_id"])
        del s["_id"]
    return students
 
 
#4.

from fastapi import Path
 
@app.get("/students/{student_id}")
def get_student_by_id(
    student_id: str = Path(..., description="MongoDB ObjectId of the student")
):
    try:
        obj_id = ObjectId(student_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid student ID")
 
    student = db.students.find_one({"_id": obj_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
 
    student["student_id"] = str(student["_id"])
    del student["_id"]
    return student
 

 #5.
from fastapi import FastAPI, HTTPException, Query

@app.get("/students/search")
def search_students(name: str = Query(..., min_length=1)):
  
    try:
        # MongoDB regex for case-insensitive partial match
        regex = re.compile(name, re.IGNORECASE)
        results = students_collection.find({"name": regex})

        students = []
        for s in results:
            s["id"] = str(s["_id"])
            del s["_id"]
            students.append(s)

        if not students:
            return {"message": "No students found"}

        return students
    except Exception as e:
        logging.error("Error searching students: %s", e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

#6.
from fastapi import FastAPI, HTTPException
from bson import ObjectId
from bson.errors import InvalidId

# Assuming you already have this
enrollments_collection = db["enrollments"]

@app.get("/enrollments/{enrollment_id}")
def get_enrollment(enrollment_id: str):
    try:
        obj_id = ObjectId(enrollment_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid enrollment ID")

    enrollment = enrollments_collection.find_one({"_id": obj_id})
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    enrollment["id"] = str(enrollment["_id"])
    del enrollment["_id"]

    return enrollment

#7.
from fastapi import Body
 
 
@app.put("/studentsnew/{student_id}")
def update_student(student_id: str, student_update: Student = Body(...)):
    try:
        obj_id = ObjectId(student_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid student ID")
 
    update_data = student_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
 
    result = db.students.update_one({"_id": obj_id}, {"$set": update_data})
 
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
 
    student = db.students.find_one({"_id": obj_id})
    student["student_id"] = str(student["_id"])
    del student["_id"]
    return student
 
 
# 8.
@app.delete("/studentsnew/{student_id}")
def delete_student(student_id: str):

    try:
        obj_id = ObjectId(student_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid student ID")
 
    student = db.students.find_one({"_id": obj_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
 
    enrollment = db.enrollments.find_one({"student_id": obj_id})
    if enrollment:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete student: student is enrolled in a course",
        )
 
    db.students.delete_one({"_id": obj_id})
    return {"message": f"Student '{student['name']}' deleted successfully"}



 #9.
@app.get("/stats/grades")
def get_grade_stats():
    pipeline = [
        {"$group": {"_id": "$grade", "count": {"$sum": 1}}}
    ]
 
    try:
        result =(get_students().aggrigate(pipeline))  
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/stats/grades")
def get_grade_stats():
    pipeline = [
        {"$group": {"_id": "$grade", "count": {"$sum": 1}}}
    ]
 
    try:
        result =(get_students().aggrigate(pipeline))  
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
# 10.
from collections import Counter
 
@app.get("/stats/top-courses")
def get_top_courses():
    try:
        enrollments = list(db.enrollments.find())
 
        course_counts = Counter(str(e["course_id"]) for e in enrollments)
 
        if not course_counts:
            return {"message": "No enrollments found"}
 
        courses = {str(c["_id"]): c for c in db.courses.find()}
 
        top_courses = []
        for course_id, count in course_counts.most_common():
            course = courses.get(course_id)
            if course:
                top_courses.append({
                    "course_id": course_id,
                    "course_name": course.get("course_name", "Unknown"),
                    "instructor": course.get("instructor", "Unknown"),
                    "enroll_count": count
                })
 
        return top_courses
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
# 11.
from fastapi import File, UploadFile
import pandas as pd
import io
 
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
 
        students = df.to_dict(orient="records")
 
        if not students:
            raise HTTPException(status_code=400, detail="CSV file is empty")
 
        result = db.students.insert_many(students)
 
        return {
            "message": f"{len(result.inserted_ids)} students uploaded successfully",
            "inserted_ids": [str(_id) for _id in result.inserted_ids]
        }
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
     
#12.     
from fastapi import FastAPI, File, UploadFile, HTTPException
from pymongo import MongoClient
import pandas as pd
import io

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["school_db"]
students_collection = db["students"]

# ---------- POST /upload-csv ----------
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    # Check file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        # Read file contents
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        # Validate required columns
        required_columns = {"name", "age", "grade", "email"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain columns: {', '.join(required_columns)}"
            )

        # Convert DataFrame to dictionary list
        records = df.to_dict(orient="records")

        # Insert into MongoDB
        if records:
            students_collection.insert_many(records)

        return {"message": f"Inserted {len(records)} students successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/upload-csv")
def upload_csv_info():
    return {"message": "Use POST /upload-csv with a CSV file to upload students"}

#15.
from fastapi import FastAPI, Depends, Header, HTTPException
from pymongo import MongoClient

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["school_db"]
students_collection = db["students"]

# ---------------- API KEY CONFIG ----------------
API_KEY = "secret123"
API_KEY_NAME = "x-api-key"

def api_key_auth(x_api_key: str = Header(...)):
    """Dependency that checks for correct API key"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return True

# ---------------- SECURE ROUTES ----------------
@app.get("/secure/students", dependencies=[Depends(api_key_auth)])
def get_secure_students():
    """Return all students (only accessible with API key)"""
    students = list(students_collection.find())
    for s in students:
        s["id"] = str(s["_id"])
        del s["_id"]
    return students

@app.get("/secure/databases", dependencies=[Depends(api_key_auth)])
def get_secure_databases():
    """Return all MongoDB databases (only accessible with API key)"""
    return {"databases": client.list_database_names()}
    