-- ============================================================
-- QUERIES FOR FITNESS CLASS BOOKING
-- ============================================================


-- Q1: How many spots are still open in each upcoming class?
-- WHY: A member needs to know if a class is full before trying to book.
-- The manager also uses this to see which classes are popular.

SELECT c.class_id, ct.name AS class_name, c.schedule_date,
       c.capacity - COUNT(b.booking_id) AS spots_remaining
FROM classes c
JOIN class_types ct ON c.class_type_id = ct.class_type_id
LEFT JOIN bookings b ON c.class_id = b.class_id
GROUP BY c.class_id
ORDER BY c.schedule_date;

-- Q2: What is the attendance rate for each class type?
-- WHY: The gym manager needs to know which classes people actually
-- show up to (vs. just booking). Low attendance might mean
-- the class time or instructor isn't working.

SELECT ct.name AS class_type,
       COUNT(att.booking_id) AS total_bookings,
       SUM(att.attended) AS total_attended,
       ROUND(100.0 * SUM(att.attended) / COUNT(att.booking_id), 1) AS attendance_pct
FROM class_types ct
JOIN classes c ON ct.class_type_id = c.class_type_id
JOIN bookings b ON c.class_id = b.class_id
JOIN attendance att ON b.booking_id = att.booking_id
GROUP BY ct.class_type_id
ORDER BY attendance_pct DESC;

-- Q3: Which members have the most no-shows?
-- WHY: The gym may want to follow up with frequent no-shows
-- (e.g. send reminders or apply a no-show policy)
-- to free up spots for other members.

SELECT m.name, COUNT(*) AS no_shows
FROM members m
JOIN bookings b ON m.member_id = b.member_id
JOIN attendance att ON b.booking_id = att.booking_id
WHERE att.attended = 0
GROUP BY m.member_id
ORDER BY no_shows DESC;

-- Q4: How many classes has each member attended in total?
-- WHY: Useful for engagement tracking — the gym can identify
-- active members and those who might need encouragement.

SELECT m.name, m.membership_type, COUNT(*) AS classes_attended
FROM members m
JOIN bookings b ON m.member_id = b.member_id
JOIN attendance att ON b.booking_id = att.booking_id
WHERE att.attended = 1
GROUP BY m.member_id
ORDER BY classes_attended DESC;
