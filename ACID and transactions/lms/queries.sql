-- ============================================================
-- Online Learning Management System (LMS) -- Queries
-- ============================================================

PRAGMA foreign_keys = ON;

-- ────────────────────────────────────────────────────────────
-- QUESTION 1
-- "Which courses is a given student enrolled in, and what is
--  their current enrollment status?"
--
-- WHY: The most fundamental view a student needs — their
-- personal course list with statuses so they know what is
-- active vs. completed or dropped.
-- ────────────────────────────────────────────────────────────
SELECT
    c.title        AS course_title,
    cat.name       AS category,
    u_inst.name    AS instructor,
    e.enrolled_at,
    e.status
FROM enrollments e
JOIN courses    c     ON e.course_id = c.course_id
JOIN categories cat   ON c.category_id = cat.category_id
JOIN users      u_inst ON c.instructor_id = u_inst.user_id
WHERE e.student_id = 5   -- Diana Prince; change ID to query any student
ORDER BY e.enrolled_at;


-- ────────────────────────────────────────────────────────────
-- QUESTION 2
-- "What is the average score of each student enrolled in a
--  specific course, ranked from highest to lowest?"
--
-- WHY: Instructors need a quick grade-overview so they can
-- identify struggling students and recognise top performers.
-- ────────────────────────────────────────────────────────────
SELECT
    u.name                                              AS student,
    e.status                                            AS enrollment_status,
    COUNT(s.submission_id)                              AS submissions_graded,
    ROUND(AVG(s.score), 2)                              AS average_score,
    -- Percentage earned out of the total possible marks
    ROUND(SUM(s.score) * 100.0
          / NULLIF(SUM(a.max_score), 0), 2)             AS overall_pct
FROM enrollments e
JOIN users       u ON e.student_id = u.user_id
JOIN assignments a ON a.course_id  = e.course_id
-- LEFT JOIN so students with no submissions still appear (score will be NULL)
LEFT JOIN submissions s ON s.assignment_id = a.assignment_id
                       AND s.student_id    = e.student_id
WHERE e.course_id = 1   -- Introduction to Python; change to any course_id
GROUP BY e.student_id
ORDER BY average_score DESC NULLS LAST;


-- ────────────────────────────────────────────────────────────
-- QUESTION 3
-- "Which courses are at or near full enrollment capacity?"
--
-- WHY: Admins and instructors must monitor capacity to decide
-- whether to open additional sections or expand seats.
-- ────────────────────────────────────────────────────────────
SELECT
    c.title                                         AS course_title,
    u.name                                          AS instructor,
    c.max_enrollment                                AS capacity,
    COUNT(e.enrollment_id)                          AS enrolled_count,
    c.max_enrollment - COUNT(e.enrollment_id)       AS seats_remaining,
    ROUND(COUNT(e.enrollment_id) * 100.0
          / c.max_enrollment, 1)                    AS fill_pct
FROM courses    c
JOIN users      u ON c.instructor_id = u.user_id
-- Only count students who have NOT dropped
LEFT JOIN enrollments e ON e.course_id = c.course_id
                       AND e.status   != 'dropped'
GROUP BY c.course_id
ORDER BY fill_pct DESC;


-- ============================================================
-- TRANSACTIONS
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- TRANSACTION 1 — Enrolling a student in a course
--
-- WHY we use a transaction here:
--   Two concurrent users could both pass a capacity check at
--   the same instant and both insert, pushing the course over
--   its seat limit.  By combining the capacity check and the
--   INSERT into one atomic statement (INSERT…SELECT…WHERE),
--   the guard and the write are inseparable — the row is only
--   inserted when both conditions are true at the exact moment
--   of the write.
--
-- BOTH  conditions should pass:
--     1. The course still has at least one seat free.
--     2. The student is not already actively enrolled.
--   If either check fails, the SELECT returns nothing and zero
--   rows are inserted — no error, detectable via rows-affected.
-- ────────────────────────────────────────────────────────────
BEGIN TRANSACTION;

-- Single atomic statement: capacity check + duplicate guard + insert.
-- Enrolling Ivan Petrov (student_id = 10) into Web Design (course_id = 3).
INSERT INTO enrollments (student_id, course_id, enrolled_at, status)
SELECT
    10,               -- Ivan Petrov
    3,                -- Web Design Basics
    datetime('now'),
    'active'
WHERE
    -- Condition 1: course must have at least one seat remaining.
    -- Counts active (non-dropped) enrollments and compares to cap.
    (
        SELECT c.max_enrollment - COUNT(e.enrollment_id)
        FROM   courses    c
        LEFT JOIN enrollments e ON e.course_id = c.course_id
                               AND e.status   != 'dropped'
        WHERE  c.course_id = 3
        GROUP BY c.course_id
    ) > 0
    -- Condition 2: student must not already be actively enrolled.
    -- Prevents a duplicate row for the same student/course pair.
    AND NOT EXISTS (
        SELECT 1
        FROM   enrollments
        WHERE  student_id = 10
          AND  course_id  = 3
          AND  status    != 'dropped'
    );

COMMIT;


-- ────────────────────────────────────────────────────────────
-- TRANSACTION 2 — Recording a grade for a submission
--
-- WHY we use a transaction here:
--   Grading updates the submission score AND may update the
--   enrollment status to 'completed' if all assignments are
--   now graded.  Both changes must succeed together or not at
--   all — a partial write (score saved, status not updated)
--   would leave the record inconsistent.
-- ────────────────────────────────────────────────────────────
BEGIN TRANSACTION;

-- Step 1: Save the grade and feedback for a specific submission
UPDATE submissions
SET score    = 91,
    feedback = 'Well structured, excellent use of list comprehensions'
WHERE assignment_id = 3    -- File Parsing Assignment (Course 1)
  AND student_id    = 5;   -- Diana Prince

-- Step 2: If this was the last ungraded assignment for this student
-- in the course, mark the enrollment as completed.
UPDATE enrollments
SET status = 'completed'
WHERE student_id = 5
  AND course_id  = 1
  -- Only flip status when every submission in this course is now scored
  AND NOT EXISTS (
      SELECT 1
      FROM   assignments  a
      JOIN   submissions  s ON s.assignment_id = a.assignment_id
                           AND s.student_id    = 5
      WHERE  a.course_id = 1
        AND  s.score IS NULL
  );

COMMIT;
