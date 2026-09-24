-- ============================================================
-- Online Learning Management System (LMS) -- Schema
-- ============================================================

-- Enable foreign key enforcement in SQLite
PRAGMA foreign_keys = ON;

-- Users table covers all roles: students, instructors, admins
CREATE TABLE users (
    user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    role       TEXT    NOT NULL CHECK(role IN ('student', 'instructor', 'admin')),
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Categories classify courses by subject area
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE
);

-- Courses belong to one instructor and one category
CREATE TABLE courses (
    course_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    title          TEXT    NOT NULL,
    description    TEXT,
    instructor_id  INTEGER NOT NULL,
    category_id    INTEGER NOT NULL,
    start_date     TEXT    NOT NULL,
    end_date       TEXT    NOT NULL,
    max_enrollment INTEGER NOT NULL DEFAULT 30,
    price          REAL    NOT NULL DEFAULT 0.00,
    FOREIGN KEY (instructor_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id)  REFERENCES categories(category_id)
);

-- Enrollments link students to courses; enforces one enrollment per student per course
CREATE TABLE enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    INTEGER NOT NULL,
    course_id     INTEGER NOT NULL,
    enrolled_at   TEXT    NOT NULL DEFAULT (datetime('now')),
    status        TEXT    NOT NULL DEFAULT 'active'
                          CHECK(status IN ('active', 'completed', 'dropped')),
    UNIQUE(student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    FOREIGN KEY (course_id)  REFERENCES courses(course_id)
);

-- Lessons are the individual content units within a course, ordered by order_num
CREATE TABLE lessons (
    lesson_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id        INTEGER NOT NULL,
    title            TEXT    NOT NULL,
    content_url      TEXT,
    duration_minutes INTEGER,
    order_num        INTEGER NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Assignments are graded tasks tied to a specific course
CREATE TABLE assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id     INTEGER NOT NULL,
    title         TEXT    NOT NULL,
    description   TEXT,
    due_date      TEXT    NOT NULL,
    max_score     REAL    NOT NULL DEFAULT 100,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Submissions record each student's attempt at an assignment (one per student per assignment)
CREATE TABLE submissions (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    student_id    INTEGER NOT NULL,
    submitted_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    score         REAL,                -- NULL means not yet graded
    feedback      TEXT,
    UNIQUE(assignment_id, student_id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id),
    FOREIGN KEY (student_id)   REFERENCES users(user_id)
);
