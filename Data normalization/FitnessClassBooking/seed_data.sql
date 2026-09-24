-- Mock data for Fitness Class Booking

-- Instructors (4 rows)
INSERT INTO instructors (name, specialty) VALUES ('Maria Lopez', 'Yoga');
INSERT INTO instructors (name, specialty) VALUES ('James Park', 'Spinning');
INSERT INTO instructors (name, specialty) VALUES ('Aisha Khan', 'HIIT');
INSERT INTO instructors (name, specialty) VALUES ('Tom Reed', 'Pilates');

-- Class types (4 rows)
INSERT INTO class_types (name, description) VALUES ('Yoga', 'Flexibility and mindfulness');
INSERT INTO class_types (name, description) VALUES ('Spinning', 'High-intensity cycling workout');
INSERT INTO class_types (name, description) VALUES ('HIIT', 'High-Intensity Interval Training');
INSERT INTO class_types (name, description) VALUES ('Pilates', 'Core strength and posture');

-- Classes (8 scheduled sessions)
INSERT INTO classes (class_type_id, instructor_id, schedule_date, start_time, capacity) VALUES (1, 1, '2026-02-02', '09:00', 15);
INSERT INTO classes (class_type_id, instructor_id, schedule_date, start_time, capacity) VALUES (2, 2, '2026-02-02', '10:00', 20);
INSERT INTO classes (class_type_id, instructor_id, schedule_date, start_time, capacity) VALUES (3, 3, '2026-02-03', '08:00', 25);
INSERT INTO classes (class_type_id, instructor_id, schedule_date, start_time, capacity) VALUES (1, 1, '2026-02-05', '09:00', 15);
INSERT INTO classes (class_type_id, instructor_id, schedule_date, start_time, capacity) VALUES (4, 4, '2026-02-05', '11:00', 12);
INSERT INTO classes (class_type_id, instructor_id, schedule_date, start_time, capacity) VALUES (2, 2, '2026-02-07', '10:00', 20);
INSERT INTO classes (class_type_id, instructor_id, schedule_date, start_time, capacity) VALUES (3, 3, '2026-02-09', '08:00', 25);
INSERT INTO classes (class_type_id, instructor_id, schedule_date, start_time, capacity) VALUES (4, 4, '2026-02-10', '11:00', 12);

-- Members (6 rows)
INSERT INTO members (name, email, membership_type) VALUES ('Lena Kim', 'lena@example.com', 'Premium');
INSERT INTO members (name, email, membership_type) VALUES ('Marco Rossi', 'marco@example.com', 'Basic');
INSERT INTO members (name, email, membership_type) VALUES ('Priya Sharma', 'priya@example.com', 'Premium');
INSERT INTO members (name, email, membership_type) VALUES ('Jake Miller', 'jake@example.com', 'Basic');
INSERT INTO members (name, email, membership_type) VALUES ('Sara Chen', 'sara@example.com', 'Premium');
INSERT INTO members (name, email, membership_type) VALUES ('Omar Ali', 'omar@example.com', 'Basic');

-- Bookings (15 rows)
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (1, 1, '2026-01-30');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (1, 2, '2026-01-31');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (1, 3, '2026-02-01');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (2, 4, '2026-01-31');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (2, 5, '2026-02-01');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (3, 1, '2026-02-01');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (3, 6, '2026-02-02');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (4, 2, '2026-02-03');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (4, 3, '2026-02-04');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (5, 5, '2026-02-03');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (5, 6, '2026-02-04');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (6, 1, '2026-02-05');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (7, 3, '2026-02-07');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (7, 4, '2026-02-08');
INSERT INTO bookings (class_id, member_id, booking_date) VALUES (8, 5, '2026-02-09');

-- Attendance (15 rows — one per booking)
INSERT INTO attendance (booking_id, attended) VALUES (1, 1);
INSERT INTO attendance (booking_id, attended) VALUES (2, 1);
INSERT INTO attendance (booking_id, attended) VALUES (3, 0);  -- no-show
INSERT INTO attendance (booking_id, attended) VALUES (4, 1);
INSERT INTO attendance (booking_id, attended) VALUES (5, 1);
INSERT INTO attendance (booking_id, attended) VALUES (6, 1);
INSERT INTO attendance (booking_id, attended) VALUES (7, 0);  -- no-show
INSERT INTO attendance (booking_id, attended) VALUES (8, 1);
INSERT INTO attendance (booking_id, attended) VALUES (9, 1);
INSERT INTO attendance (booking_id, attended) VALUES (10, 1);
INSERT INTO attendance (booking_id, attended) VALUES (11, 1);
INSERT INTO attendance (booking_id, attended) VALUES (12, 1);
INSERT INTO attendance (booking_id, attended) VALUES (13, 1);
INSERT INTO attendance (booking_id, attended) VALUES (14, 0);  -- no-show
INSERT INTO attendance (booking_id, attended) VALUES (15, 1);
