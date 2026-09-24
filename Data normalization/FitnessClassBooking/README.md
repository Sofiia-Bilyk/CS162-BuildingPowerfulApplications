# Fitness Class Booking and Attendance Tracking

A database for a gym that manages fitness class schedules, member bookings, and attendance tracking. 

## Tables

- **instructors** — Gym instructors with their name and specialty area.
- **class_types** — Types of classes offered (e.g. Yoga, HIIT) with a description. Normalized out so the same class type isn't repeated across every session.
- **classes** — A specific scheduled session with a date, time, instructor, and capacity limit.
- **members** — Gym members with name, email, and membership tier (Basic/Premium).
- **bookings** — Links a member to a class they signed up for. Has a **composite unique constraint** `(class_id, member_id)` to prevent double-booking.
- **attendance** — Records whether a booked member actually showed up (1) or was a no-show (0).

## Schema Diagram

```
FITNESS CLASS BOOKING — SCHEMA DIAGRAM 
===============================================

  +----------------+      +----------------+
  | instructors    |      | class_types    |
  +----------------+      +----------------+
  |instructor_id PK|      |class_type_id PK|
  | name           |      | name           |
  | specialty      |      | description    |
  +---------------+       +--------------+
        |                       |
        | 1:N                   | 1:N
        |                       |
  +-----v-----------------------v-----+
  |             classes               |
  +-----------------------------------+
  | class_id         PK               |
  | class_type_id    FK -> class_types|
  | instructor_id    FK -> instructors|
  | schedule_date                     |
  | start_time                        |
  | capacity                          |
  +-----------------------------------+
              |
              | 1:N
              |
  +-----------v-----------+       +------------+
  |       bookings        |       |  members   |
  +-----------------------+       +------------+
  | booking_id    PK      |       |member_id PK|
  | class_id      FK  ----+       | name       |
  | member_id     FK  ----------->| email      |
  | booking_date          |       |membership_ |
  | UNIQUE(class_id,      |       |  type      |
  |        member_id)     |       +------------+
  +-----------+-----------+
              |
              | 1:1
              |
  +-----------v-----------+
  |      attendance       |
  +-----------------------+
  | booking_id  PK, FK    |
  | attended (0 or 1)     |
  +-----------------------+


To DENORMALIZE (move to lower normal form):
- Embed class_type_name and instructor_name directly into classes table
- Merge attendance into bookings as an extra column
```
