-- Fitness Class Booking and Attendance Tracking

-- Instructors table: stores instructor details separately
CREATE TABLE instructors (
    instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialty TEXT
);

-- Class_types table: defines types of fitness classes (e.g. Yoga, Spinning)
CREATE TABLE class_types (
    class_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Classes table: a specific scheduled class session
-- Each class has a type, an instructor, a date/time, and a capacity
CREATE TABLE classes (
    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_type_id INTEGER NOT NULL,
    instructor_id INTEGER NOT NULL,
    schedule_date TEXT NOT NULL,   -- ISO date e.g. '2026-02-10'
    start_time TEXT NOT NULL,      -- e.g. '09:00'
    capacity INTEGER NOT NULL,
    FOREIGN KEY (class_type_id) REFERENCES class_types(class_type_id),
    FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
);

-- Members table: gym members who can book classes
CREATE TABLE members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    membership_type TEXT NOT NULL  -- e.g. 'Basic', 'Premium'
);

-- Bookings table: a member books a spot in a class
-- Composite key ensures a member can't book the same class twice
CREATE TABLE bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,    -- when the booking was made
    UNIQUE(class_id, member_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- Attendance table: tracks whether a booked member actually showed up
CREATE TABLE attendance (
    booking_id INTEGER PRIMARY KEY,
    attended INTEGER NOT NULL DEFAULT 0,  -- 0 = no-show, 1 = attended
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);
