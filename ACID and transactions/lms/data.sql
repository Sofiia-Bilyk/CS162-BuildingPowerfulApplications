-- ============================================================
-- Online Learning Management System (LMS) -- Mock Data
-- ============================================================

PRAGMA foreign_keys = ON;

-- ── Users ────────────────────────────────────────────────────
INSERT INTO users (name, email, role) VALUES
    ('Admin User',      'admin@lms.edu',         'admin'),
    ('Alice Johnson',   'alice.j@lms.edu',        'instructor'),
    ('Bob Martinez',    'bob.m@lms.edu',          'instructor'),
    ('Carol Chen',      'carol.c@lms.edu',        'instructor'),
    ('Diana Prince',    'diana.p@students.edu',   'student'),
    ('Ethan Lee',       'ethan.l@students.edu',   'student'),
    ('Fiona Green',     'fiona.g@students.edu',   'student'),
    ('George Kim',      'george.k@students.edu',  'student'),
    ('Hannah Scott',    'hannah.s@students.edu',  'student'),
    ('Ivan Petrov',     'ivan.p@students.edu',    'student'),
    ('Julia Adams',     'julia.a@students.edu',   'student'),
    ('Kevin Brown',     'kevin.b@students.edu',   'student');

-- ── Categories ───────────────────────────────────────────────
INSERT INTO categories (name) VALUES
    ('Programming'),
    ('Data Science'),
    ('Web Design'),
    ('Business Analytics'),
    ('Mathematics');

-- ── Courses ──────────────────────────────────────────────────
-- instructor_id: Alice=2, Bob=3, Carol=4
INSERT INTO courses (title, description, instructor_id, category_id, start_date, end_date, max_enrollment, price) VALUES
    ('Introduction to Python',          'Learn Python from scratch',                  2, 1, '2026-01-10', '2026-03-10', 30, 199.00),
    ('Machine Learning Fundamentals',   'Practical ML with scikit-learn',             3, 2, '2026-01-15', '2026-04-15', 20, 349.00),
    ('Web Design Basics',               'HTML, CSS, and responsive design',           4, 3, '2026-02-01', '2026-04-01', 25, 149.00),
    ('Business Analytics with SQL',     'Data-driven business decisions using SQL',   3, 4, '2026-02-01', '2026-04-30', 20, 249.00),
    ('Linear Algebra for Data Science', 'Vectors, matrices, and transformations',     2, 5, '2026-01-20', '2026-03-20', 15, 199.00);

-- ── Enrollments ──────────────────────────────────────────────
-- student IDs: Diana=5, Ethan=6, Fiona=7, George=8, Hannah=9, Ivan=10, Julia=11, Kevin=12
INSERT INTO enrollments (student_id, course_id, enrolled_at, status) VALUES
    (5,  1, '2026-01-09', 'active'),
    (5,  3, '2026-01-30', 'active'),
    (6,  1, '2026-01-09', 'active'),
    (6,  2, '2026-01-14', 'active'),
    (7,  1, '2026-01-09', 'completed'),
    (7,  4, '2026-01-31', 'active'),
    (8,  2, '2026-01-14', 'active'),
    (8,  5, '2026-01-19', 'active'),
    (9,  3, '2026-01-30', 'active'),
    (9,  4, '2026-01-31', 'active'),
    (10, 1, '2026-01-10', 'dropped'),
    (10, 2, '2026-01-14', 'active'),
    (11, 4, '2026-02-01', 'active'),
    (11, 5, '2026-01-19', 'active'),
    (12, 3, '2026-02-01', 'active'),
    (12, 5, '2026-01-20', 'active');

-- ── Lessons ───────────────────────────────────────────────────
-- Course 1: Intro to Python
INSERT INTO lessons (course_id, title, content_url, duration_minutes, order_num) VALUES
    (1, 'Variables and Data Types',   'https://lms.edu/py/lesson1', 45, 1),
    (1, 'Control Flow',               'https://lms.edu/py/lesson2', 50, 2),
    (1, 'Functions and Modules',      'https://lms.edu/py/lesson3', 60, 3),
    (1, 'File I/O and Exceptions',    'https://lms.edu/py/lesson4', 55, 4);

-- Course 2: Machine Learning
INSERT INTO lessons (course_id, title, content_url, duration_minutes, order_num) VALUES
    (2, 'What is Machine Learning?',  'https://lms.edu/ml/lesson1', 40, 1),
    (2, 'Linear Regression',          'https://lms.edu/ml/lesson2', 65, 2),
    (2, 'Classification Algorithms',  'https://lms.edu/ml/lesson3', 70, 3);

-- Course 3: Web Design
INSERT INTO lessons (course_id, title, content_url, duration_minutes, order_num) VALUES
    (3, 'HTML Structure',             'https://lms.edu/web/lesson1', 40, 1),
    (3, 'CSS Styling',                'https://lms.edu/web/lesson2', 50, 2),
    (3, 'Responsive Layouts',         'https://lms.edu/web/lesson3', 55, 3);

-- Course 4: Business Analytics
INSERT INTO lessons (course_id, title, content_url, duration_minutes, order_num) VALUES
    (4, 'SQL SELECT Basics',          'https://lms.edu/ba/lesson1', 45, 1),
    (4, 'Joins and Aggregations',     'https://lms.edu/ba/lesson2', 60, 2),
    (4, 'Dashboards and Reporting',   'https://lms.edu/ba/lesson3', 55, 3);

-- Course 5: Linear Algebra
INSERT INTO lessons (course_id, title, content_url, duration_minutes, order_num) VALUES
    (5, 'Vectors and Spaces',         'https://lms.edu/la/lesson1', 50, 1),
    (5, 'Matrix Operations',          'https://lms.edu/la/lesson2', 60, 2),
    (5, 'Eigenvalues and Eigenvectors','https://lms.edu/la/lesson3', 65, 3);

-- ── Assignments ──────────────────────────────────────────────
INSERT INTO assignments (course_id, title, description, due_date, max_score) VALUES
    (1, 'Python Basics Quiz',       'Multiple-choice quiz on variables and control flow', '2026-01-25', 100),
    (1, 'Functions Project',        'Implement a small library of utility functions',      '2026-02-10', 100),
    (1, 'File Parsing Assignment',  'Read and process a CSV file with Python',            '2026-03-01', 100),
    (2, 'Regression Notebook',      'Build a linear regression model on housing data',    '2026-02-20', 100),
    (2, 'Classification Report',    'Implement and evaluate a classifier',                '2026-03-15', 100),
    (3, 'Portfolio Page',           'Build a personal portfolio using HTML/CSS',          '2026-02-28', 100),
    (3, 'Responsive Redesign',      'Make an existing page mobile-responsive',            '2026-03-20', 100),
    (4, 'SQL Query Set',            'Answer 10 business questions using SQL',             '2026-02-28', 100),
    (4, 'Analytics Dashboard',      'Create an interactive sales report',                 '2026-04-10', 100),
    (5, 'Matrix Operations HW',     'Solve 15 matrix computation problems',               '2026-02-15', 100),
    (5, 'Eigenvalue Application',   'Apply eigenvalue decomposition to a dataset',        '2026-03-10', 100);

-- ── Submissions ──────────────────────────────────────────────
-- assignment_id: Python=1,2,3 | ML=4,5 | Web=6,7 | BA=8,9 | LA=10,11
-- Enrolled students submit their assignments (some graded, some not yet)

INSERT INTO submissions (assignment_id, student_id, submitted_at, score, feedback) VALUES
    -- Diana (5): Python and Web Design
    (1,  5, '2026-01-24', 88, 'Good work, minor errors in loops'),
    (2,  5, '2026-02-09', 92, 'Clean, well-documented code'),
    (6,  5, '2026-02-27', 79, 'Nice layout but missing a contact section'),
    -- Ethan (6): Python and ML
    (1,  6, '2026-01-23', 95, 'Excellent, full marks on most sections'),
    (2,  6, '2026-02-08', 87, 'Good structure, refactor the helper function'),
    (4,  6, '2026-02-19', 90, 'Strong regression analysis'),
    -- Fiona (7): Python (completed) and Business Analytics
    (1,  7, '2026-01-22', 100, 'Perfect score'),
    (2,  7, '2026-02-07', 98,  'Outstanding work'),
    (3,  7, '2026-02-28', 95,  'Great file parsing logic'),
    (8,  7, '2026-02-27', 82, 'Correct queries but missing comments'),
    -- George (8): ML and Linear Algebra
    (4,  8, '2026-02-18', 78, 'Model works but overfitting concerns'),
    (10, 8, '2026-02-14', 85, 'Mostly correct, watch matrix dimensions'),
    -- Hannah (9): Web Design and Business Analytics
    (6,  9, '2026-02-26', 91, 'Beautiful portfolio!'),
    (7,  9, '2026-03-18', 88, 'Responsive layout works on all breakpoints'),
    (8,  9, '2026-02-26', 76, 'Some queries are inefficient, use JOINs'),
    -- Ivan (10): ML only (active)
    (4, 10, '2026-02-20', 83, 'Good effort, review gradient descent'),
    -- Julia (11): Business Analytics and Linear Algebra
    (8, 11, '2026-02-27', 94, 'Excellent SQL, creative approach'),
    (10,11, '2026-02-14', 92, 'Very clean solutions'),
    (11,11, '2026-03-09', 88, 'Good real-world application'),
    -- Kevin (12): Web Design and Linear Algebra
    (6, 12, '2026-02-28', 73, 'Functional but plain styling'),
    (10,12, '2026-02-13', 80, 'Watch out for transpose errors');
