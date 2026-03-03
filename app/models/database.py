import sqlite3
from pathlib import Path

from flask import current_app, g


SCHEMA = """
CREATE TABLE IF NOT EXISTS student_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    cgpa REAL NOT NULL,
    skills TEXT NOT NULL,
    interests TEXT NOT NULL,
    career_preference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    if "db" not in g:
        db_path = Path(current_app.root_path).parent / current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        db.commit()
    app.teardown_appcontext(close_db)


def save_student_profile(profile: dict) -> int:
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO student_profiles (name, department, cgpa, skills, interests, career_preference)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            profile["name"],
            profile["department"],
            profile["cgpa"],
            profile["skills"],
            profile["interests"],
            profile.get("career_preference"),
        ),
    )
    db.commit()
    return cursor.lastrowid
