# Import FastAPI Library
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Extra

class Student(BaseModel):
    name: str
    age: int

    class Config:
        extra = Extra.forbid # reject the undeclared fields


# Create an app object
app = FastAPI() 


# Define a GET endpoint at "/"
@app.get("/")  # decorator defines a route
def read_root():
    return {"message": "Hello, welcome to AR Tech 🥳"}


# Port 8000 is DEFAULT for FastAPi/Uvicorn


# Path Parameter Example
# Parameters that are part of the URL path
@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello {name}, welcome to AR Tech!"}


# Query Parameter Example
# Parameters given after `?` in URL, like extra details
@app.get("/add")
def add(x: int, y: int, z: int):
    return {"sum": x + y + z}


# Mixed Path + Query Parameters
@app.get("/students/{student_id}")
def student_details(student_id: int, subject: str = "Math"):
    return {"student_id": student_id, "subject": subject}


@app.post("/students")
def create_student(student: Student):
    return {"message": f"Student {student.name} added!"}


@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    return {"message": f"Student {student_id} updated to {student.name}!"}

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    return {"message": f"Student {student_id} deleted!"}