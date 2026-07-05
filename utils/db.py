import sqlite3
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "database.db"


def get_connection():
    DATA_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            group_name TEXT,
            subject TEXT,
            weekly_hours INTEGER,
            knowledge_level TEXT,
            learning_style TEXT,
            task_type TEXT,
            difficult_topics TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            task_title TEXT,
            answer_text TEXT,
            file_name TEXT,
            ai_score INTEGER,
            ai_feedback TEXT,
            status TEXT,
            created_at TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            deadline TEXT,
            rubric TEXT,
            created_at TEXT
        )
    """)

    def column_exists(cursor, table_name, column_name):
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns

    if not column_exists(cursor, "submissions", "file_path"):
        cursor.execute("ALTER TABLE submissions ADD COLUMN file_path TEXT")

    if not column_exists(cursor, "submissions", "file_analysis"):
        cursor.execute("ALTER TABLE submissions ADD COLUMN file_analysis TEXT")

    if not column_exists(cursor, "submissions", "extracted_text"):
        cursor.execute("ALTER TABLE submissions ADD COLUMN extracted_text TEXT")

    if not column_exists(cursor, "submissions", "drawing_overlay_path"):
        cursor.execute("ALTER TABLE submissions ADD COLUMN drawing_overlay_path TEXT")

    if not column_exists(cursor, "submissions", "drawing_score"):
        cursor.execute("ALTER TABLE submissions ADD COLUMN drawing_score INTEGER")

    conn.commit()
    conn.close()


def add_student(
    full_name,
    group_name,
    subject,
    weekly_hours,
    knowledge_level,
    learning_style,
    task_type,
    difficult_topics
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (
            full_name,
            group_name,
            subject,
            weekly_hours,
            knowledge_level,
            learning_style,
            task_type,
            difficult_topics,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        full_name,
        group_name,
        subject,
        weekly_hours,
        knowledge_level,
        learning_style,
        task_type,
        difficult_topics,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    student_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return student_id


def add_submission(
    student_id,
    task_title,
    answer_text,
    file_name=None,
    file_path=None,
    file_analysis=None,
    extracted_text=None,
    drawing_overlay_path=None,
    drawing_score=None,
    ai_score=0,
    ai_feedback="AI feedback hali ulanmagan",
    status="Yuborilgan"
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO submissions (
            student_id,
            task_title,
            answer_text,
            file_name,
            file_path,
            file_analysis,
            extracted_text,
            drawing_overlay_path,
            drawing_score,
            ai_score,
            ai_feedback,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        task_title,
        answer_text,
        file_name,
        file_path,
        file_analysis,
        extracted_text,
        drawing_overlay_path,
        drawing_score,
        ai_score,
        ai_feedback,
        status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def add_task(title, description, deadline, rubric):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (
            title,
            description,
            deadline,
            rubric,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        description,
        str(deadline),
        rubric,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_students():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM students
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_submissions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            submissions.id,
            students.full_name,
            students.group_name,
            submissions.task_title,
            submissions.answer_text,
            submissions.file_name,
            submissions.file_path,
            submissions.file_analysis,
            submissions.extracted_text,
            submissions.drawing_overlay_path,
            submissions.drawing_score,
            submissions.ai_score,
            submissions.ai_feedback,
            submissions.status,
            submissions.created_at
        FROM submissions
        LEFT JOIN students ON submissions.student_id = students.id
        ORDER BY submissions.created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_tasks():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM tasks
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows