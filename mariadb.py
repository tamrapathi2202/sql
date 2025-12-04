import streamlit as st
import mariadb
import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="localhost", user="root", password="tamrapathi3383", database="school_db"
)
cur = conn.cursor()

cur.execute("SHOW TABLES")
result = cur.fetchall()
print(result)


st.title("School DB Dashboard")

students = get_data("SELECT * FROM students")
st.dataframe(pd.DataFrame(students))

students_df = pd.read_csv("./students.csv")

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS students (
        student_id INT PRIMARY KEY,
        name VARCHAR(100),
        age INT,
        grade VARCHAR(10),
        email VARCHAR(100)
    )
"""
)

for _, row in students_df.iterrows():
    cur.execute(
        "INSERT INTO students (student_id, name, age, grade, email) VALUES (%s, %s, %s, %s, %s)",
        (row.student_id, row.name, row.age, row.grade, row.email),
    )

# ---- Load courses.csv ----
courses_df = pd.read_csv("./courses.csv")

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS courses (
        course_id INT PRIMARY KEY,
        course_name VARCHAR(100),
        instructor VARCHAR(100)
    )
"""
)

for _, row in courses_df.iterrows():
    cur.execute(
        "INSERT INTO courses (course_id, course_name, instructor) VALUES (%s, %s, %s)",
        (row.course_id, row.course_name, row.instructor),
    )

# ---- Load enrollments.csv ----
enrollments_df = pd.read_csv("./enrollments.csv")

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS enrollments (
        enroll_id INT PRIMARY KEY,
        student_id INT,
        course_id INT,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
    )
"""
)

for _, row in enrollments_df.iterrows():
    cur.execute(
        "INSERT INTO enrollments (enroll_id, student_id, course_id) VALUES (%s, %s, %s)",
        (row.enroll_id, row.student_id, row.course_id),
    )

import streamlit as st
import mysql.connector
import pandas as pd


# ----------------------------
# Database connection function
# ----------------------------
@st.cache_data
import streamlit as st
import mariadb

# -----------------------------
# Database connection function
# -----------------------------
def get_connection():
    return mariadb.connect(
        user="root",
        password="tamrapathi3383",  # change if needed
        host="localhost",
        port=3306,
        database="schools_db"       # make sure this DB exists
    )

# -----------------------------
# Query execution function
# -----------------------------
def get_data(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]  # column names
    conn.close()
    return rows, cols

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("School DB Dashboard")

# Students Table
students, student_cols = get_data("SELECT * FROM students")
st.subheader("Students")
st.dataframe(students, column_config={i: {"label": col} for i, col in enumerate(student_cols)})

# Courses Table
courses, course_cols = get_data("SELECT * FROM courses")
st.subheader("Courses")
st.dataframe(courses, column_config={i: {"label": col} for i, col in enumerate(course_cols)})

# Enrollments Table
enrollments, enroll_cols = get_data("SELECT * FROM enrollments")
st.subheader("Enrollments")
st.dataframe(enrollments, column_config={i: {"label": col} for i, col in enumerate(enroll_cols)})



# ----------------------------
# Function to fetch data
# ----------------------------
@st.cache_data
def get_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ----------------------------
# Streamlit UI
# ----------------------------
st.title("📊 School Dashboard (MariaDB)")

# Sidebar toggle
view_type = st.sidebar.radio("Choose view:", ["Tabular View", "Raw JSON"])

# Tables to display
tables = ["students", "courses", "enrollments"]

for table in tables:
    st.subheader(f"Table: {table}")

    try:
        df = get_data(f"SELECT * FROM {table}")

        if view_type == "Tabular View":
            st.dataframe(df)
            st.table(df.head(5))
        else:
            st.json(df.to_dict(orient="records"))

    except Exception as e:
        st.error(f"Error loading table {table}: {e}")
