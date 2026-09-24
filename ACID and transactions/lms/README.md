# Online Learning Management System (LMS)

A SQLite-backed database for managing online courses. It tracks who teaches and who studies, what content is delivered, what work is assigned, and how students perform. Instructors can monitor grades and completion; students can see their enrolled courses and submission status; admins can watch capacity across the platform.

---

## Tables

| Table | Purpose |
|-------|---------|
| `users` | Stores every person on the platform — students, instructors, and admins — in one table identified by `role`. A single table avoids duplication and lets the same person appear as both a student and an instructor. |
| `categories` | A lookup list of subject areas (e.g. Programming, Data Science). Keeps course classification consistent and makes category-level filtering easy. |
| `courses` | The core offering of the platform. Each course belongs to one instructor and one category, has a date range, a seat cap, and a price. |
| `enrollments` | The many-to-many link between students and courses. Records when a student joined and tracks their status (active / completed / dropped). A `UNIQUE(student_id, course_id)` constraint prevents double-enrollment. |
| `lessons` | Individual content units inside a course. Ordered by `order_num` so the curriculum always appears in the intended sequence. |
| `assignments` | Graded tasks attached to a course with a due date and maximum score. Separate from lessons so a course can have any number of assessments independently of its content units. |
| `submissions` | Records each student's response to an assignment — timestamp, score (NULL until graded), and instructor feedback. A `UNIQUE(assignment_id, student_id)` constraint ensures one submission per student per assignment. |

---

## Schema Diagram

```
ONLINE LEARNING MANAGEMENT SYSTEM — SCHEMA DIAGRAM
===================================================


  +------------------+           +----------------+
  | users            |           | categories     |
  +------------------+           +----------------+
  | user_id       PK |           | category_id PK |
  | name             |           | name           |
  | email            |           +-------+--------+
  | role             |                   |
  | created_at       |                   | 1:N
  +----+----------+--+                   |
       |          |                      |
  1:N  |     1:N  |                      |
  (stu)|  (instr) |                      |
       |          |                      |
       |   +------v-----------------------v--+
       |   |             courses             |
       |   +---------------------------------+
       |   | course_id        PK             |
       |   | instructor_id    FK -> users    |
       |   | category_id  FK -> categories   |
       |   | title                           |
       |   | start_date                      |
       |   | end_date                        |
       |   | max_enrollment                  |
       |   | price                           |
       |   +----+----------+-----------+-----+
       |        |          |           |
       |   1:N  |     1:N  |      1:N  |
       |        |          |           |
       |  +-----v--+  +----v------+  +-v----------+
       |  | lessons|  |enrollments|  |assignments |
       |  +--------+  +-----------+  +------------+
       |  |lesson_ |  |enroll_id  |  |asgn_id  PK |
       |  |id   PK |  |PK         |  |course_id FK|
       |  |course_ |  |student_id |  |title       |
       |  |id   FK |  |FK         |  |description |
       |  |title   |  |course_id  |  |due_date    |
       |  |content |  |FK         |  |max_score   |
       |  |duration|  |enrolled_at|  +-----+------+
       |  |order_  |  |status     |        |
       |  |num     |  +-----^-----+        | 1:N
       |  +--------+        |              |
       |                    |       +------v--------+
       +--------------------+       | submissions   |
                  1:N               +---------------+
                                    | sub_id     PK |
                                    | asgn_id    FK |
                                    | student_id FK |
                                    |   -> users    |
                                    | submitted_at  |
                                    | score         |
                                    | feedback      |
                                    +---------------+
```

---

