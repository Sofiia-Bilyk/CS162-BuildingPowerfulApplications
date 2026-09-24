-- ============================================================
-- Car Rental and Fleet Management Platform
-- Run with: sqlite3 car_rental.db < car_rental.sql
-- ============================================================

PRAGMA foreign_keys = ON;
.mode column
.headers on

-- ============================================================
-- SCHEMA
-- ============================================================

-- Physical locations that own and rent out vehicles.
CREATE TABLE Branch (
    branch_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    city       TEXT    NOT NULL,
    state      TEXT    NOT NULL,
    phone      TEXT    NOT NULL,
    address    TEXT    NOT NULL
);

-- Individual cars in the fleet, each assigned to a home branch.
-- status tracks the operational state: available / rented / maintenance / retired.
CREATE TABLE Vehicle (
    vehicle_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_id       INTEGER NOT NULL,
    make            TEXT    NOT NULL,
    model           TEXT    NOT NULL,
    year            INTEGER NOT NULL,
    license_plate   TEXT    NOT NULL UNIQUE,
    category        TEXT    NOT NULL CHECK(category IN
                        ('economy','compact','midsize','suv','luxury','van')),
    daily_rate      REAL    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'available'
                        CHECK(status IN ('available','rented','maintenance','retired')),
    current_mileage INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id)
);

-- People who rent vehicles. drivers_license must be unique.
CREATE TABLE Customer (
    customer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT    NOT NULL,
    last_name       TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    phone           TEXT    NOT NULL,
    drivers_license TEXT    NOT NULL UNIQUE,
    license_expiry  TEXT    NOT NULL   -- ISO-8601: YYYY-MM-DD
);

-- A booking linking a customer to a specific vehicle for a date range.
-- pickup_branch and return_branch may differ (one-way rentals).
CREATE TABLE Reservation (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id    INTEGER NOT NULL,
    vehicle_id     INTEGER NOT NULL,
    pickup_branch  INTEGER NOT NULL,
    return_branch  INTEGER NOT NULL,
    start_date     TEXT    NOT NULL,   -- ISO-8601
    end_date       TEXT    NOT NULL,
    status         TEXT    NOT NULL DEFAULT 'confirmed'
                       CHECK(status IN ('confirmed','active','completed','cancelled')),
    total_cost     REAL    NOT NULL,
    FOREIGN KEY (customer_id)   REFERENCES Customer(customer_id),
    FOREIGN KEY (vehicle_id)    REFERENCES Vehicle(vehicle_id),
    FOREIGN KEY (pickup_branch) REFERENCES Branch(branch_id),
    FOREIGN KEY (return_branch) REFERENCES Branch(branch_id)
);

-- Operational record created when the customer physically picks up the car.
-- actual_return_time and end_mileage are NULL while the rental is active.
CREATE TABLE Rental (
    rental_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id     INTEGER NOT NULL UNIQUE,
    actual_pickup_time TEXT    NOT NULL,
    actual_return_time TEXT,                   -- NULL while active
    start_mileage      INTEGER NOT NULL,
    end_mileage        INTEGER,                -- NULL while active
    extra_charges      REAL    NOT NULL DEFAULT 0.0,
    notes              TEXT,
    FOREIGN KEY (reservation_id) REFERENCES Reservation(reservation_id)
);

-- Every service event for a vehicle (oil changes, inspections, etc.).
-- next_service_mileage lets fleet managers know when the car needs service again.
CREATE TABLE MaintenanceRecord (
    record_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id           INTEGER NOT NULL,
    service_date         TEXT    NOT NULL,
    service_type         TEXT    NOT NULL,
    cost                 REAL    NOT NULL,
    mileage_at_service   INTEGER NOT NULL,
    next_service_mileage INTEGER NOT NULL,
    technician           TEXT    NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

-- Financial transaction tied to a reservation.
-- A reservation may have one completed payment plus a possible refund record.
CREATE TABLE Payment (
    payment_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    amount         REAL    NOT NULL,
    payment_date   TEXT    NOT NULL,
    method         TEXT    NOT NULL
                       CHECK(method IN ('credit_card','debit_card','cash','bank_transfer')),
    status         TEXT    NOT NULL DEFAULT 'completed'
                       CHECK(status IN ('pending','completed','refunded','failed')),
    FOREIGN KEY (reservation_id) REFERENCES Reservation(reservation_id)
);

-- ============================================================
-- INDEXES
-- Created before data inserts so each insert incrementally
-- maintains the index rather than requiring a full rebuild.
-- ============================================================

-- Q1 availability query: filter fleet by branch AND operational status in one seek.
-- Without this, SQLite must scan all vehicles and test branch_id then status per row.
CREATE INDEX idx_vehicle_branch_status
    ON Vehicle(branch_id, status);

-- Q3 maintenance-due query: allows direct seek to a vehicle's service history
-- and sorted traversal to find the most recent record without a full-table sort.
CREATE INDEX idx_maintenance_vehicle_date
    ON MaintenanceRecord(vehicle_id, service_date);

-- Q1 overlap detection: given a vehicle_id the index delivers its reservations
-- in start_date order, so the date-range overlap check hits only a narrow slice.
CREATE INDEX idx_reservation_vehicle_dates
    ON Reservation(vehicle_id, start_date, end_date);

-- Q4 customer history: jump straight to all reservations for one customer.
CREATE INDEX idx_reservation_customer
    ON Reservation(customer_id);

-- Q2 revenue report: filter + group by branch and date without touching
-- reservations outside the requested time window.
CREATE INDEX idx_reservation_branch_date
    ON Reservation(pickup_branch, start_date);

-- General operational filter (e.g. count active rentals fleet-wide).
CREATE INDEX idx_reservation_status
    ON Reservation(status);

-- Q2 + Q4 payment join: avoids full Payment scan when joining by reservation_id.
CREATE INDEX idx_payment_reservation
    ON Payment(reservation_id);

-- ============================================================
-- DATA
-- ============================================================

INSERT INTO Branch (name, city, state, phone, address) VALUES
    ('LAX Airport',          'Los Angeles',  'CA', '555-0101', '1 World Way, Los Angeles'),
    ('SFO Airport',          'San Francisco', 'CA', '555-0202', '780 McDonnell Rd, San Francisco'),
    ('Downtown San Diego',   'San Diego',    'CA', '555-0303', '100 Harbor Dr, San Diego');

-- branch 1 = LAX (vehicles 1,2,3,10)
-- branch 2 = SFO (vehicles 4,5,6)
-- branch 3 = San Diego (vehicles 7,8,9)
-- Vehicles 1 and 7 are overdue for maintenance (see MaintenanceRecord).
INSERT INTO Vehicle (branch_id, make, model, year, license_plate, category, daily_rate, status, current_mileage) VALUES
    (1, 'Toyota',     'Camry',          2023, '7ABC123', 'economy',  45.00, 'available',    27500),
    (1, 'Honda',      'Civic',          2022, '7DEF456', 'compact',  39.00, 'rented',       45200),
    (1, 'Ford',       'Explorer',       2024, '7GHI789', 'suv',      89.00, 'available',    12000),
    (2, 'BMW',        '5 Series',       2023, '7JKL012', 'luxury',   149.00,'available',    18000),
    (2, 'Toyota',     'RAV4',           2022, '7MNO345', 'suv',      75.00, 'rented',       38000),
    (2, 'Hyundai',    'Elantra',        2024, '7PQR678', 'compact',  42.00, 'maintenance',  52000),
    (3, 'Chevrolet',  'Malibu',         2023, '7STU901', 'midsize',  55.00, 'available',    33200),
    (3, 'Dodge',      'Grand Caravan',  2022, '7VWX234', 'van',      95.00, 'available',    41000),
    (3, 'Toyota',     'Corolla',        2021, '7YZA567', 'economy',  38.00, 'available',    62000),
    (1, 'Tesla',      'Model 3',        2024, '7BCD890', 'luxury',   175.00,'available',     8000);

INSERT INTO Customer (first_name, last_name, email, phone, drivers_license, license_expiry) VALUES
    ('Alice',   'Johnson', 'alice@email.com',   '555-1001', 'DL-100001', '2028-05-15'),
    ('Bob',     'Martinez','bob@email.com',     '555-1002', 'DL-100002', '2027-09-20'),
    ('Carol',   'White',   'carol@email.com',   '555-1003', 'DL-100003', '2026-11-30'),
    ('David',   'Lee',     'david@email.com',   '555-1004', 'DL-100004', '2029-03-10'),
    ('Emma',    'Wilson',  'emma@email.com',    '555-1005', 'DL-100005', '2027-07-22'),
    ('Frank',   'Davis',   'frank@email.com',   '555-1006', 'DL-100006', '2026-04-18'),
    ('Grace',   'Kim',     'grace@email.com',   '555-1007', 'DL-100007', '2028-12-01'),
    ('Henry',   'Brown',   'henry@email.com',   '555-1008', 'DL-100008', '2027-06-14');

-- total_cost = daily_rate * (end_date - start_date) in days
INSERT INTO Reservation (customer_id, vehicle_id, pickup_branch, return_branch, start_date, end_date, status, total_cost) VALUES
    (1, 1,  1, 1, '2025-06-01', '2025-06-05', 'completed', 180.00),  -- 4 days * $45
    (2, 3,  1, 1, '2025-06-10', '2025-06-15', 'completed', 445.00),  -- 5 days * $89
    (3, 4,  2, 2, '2025-06-15', '2025-06-18', 'completed', 447.00),  -- 3 days * $149
    (1, 7,  3, 3, '2025-07-04', '2025-07-08', 'completed', 220.00),  -- 4 days * $55
    (4, 9,  3, 3, '2025-07-20', '2025-07-25', 'completed', 190.00),  -- 5 days * $38
    (5, 1,  1, 1, '2025-08-01', '2025-08-03', 'completed',  90.00),  -- 2 days * $45
    (6, 2,  1, 1, '2026-02-20', '2026-02-26', 'active',    234.00),  -- 6 days * $39
    (7, 5,  2, 2, '2026-02-22', '2026-02-27', 'active',    375.00),  -- 5 days * $75
    (8, 10, 1, 1, '2026-03-01', '2026-03-05', 'confirmed', 700.00),  -- 4 days * $175
    (3, 4,  2, 2, '2026-03-10', '2026-03-14', 'confirmed', 596.00),  -- 4 days * $149
    (4, 8,  3, 3, '2025-09-15', '2025-09-20', 'cancelled', 475.00),  -- 5 days * $95
    (2, 3,  1, 1, '2026-04-05', '2026-04-08', 'confirmed', 267.00);  -- 3 days * $89

-- Rentals exist for all reservations that were active or completed (1-8).
INSERT INTO Rental (reservation_id, actual_pickup_time, actual_return_time, start_mileage, end_mileage, extra_charges, notes) VALUES
    (1, '2025-06-01 09:15', '2025-06-05 10:00', 23000, 23350,  0.00, NULL),
    (2, '2025-06-10 11:30', '2025-06-15 12:00', 11500, 12000, 50.00, 'Fuel surcharge: returned below half tank'),
    (3, '2025-06-15 14:00', '2025-06-18 13:30', 18000, 18280,  0.00, NULL),
    (4, '2025-07-04 10:00', '2025-07-08 11:00', 28500, 28850, 25.00, 'Minor door ding noted at return'),
    (5, '2025-07-20 09:00', '2025-07-25 10:00', 61000, 61620,  0.00, NULL),
    (6, '2025-08-01 08:00', '2025-08-03 09:00', 44500, 44800,  0.00, NULL),
    (7, '2026-02-20 10:00', NULL,                44800, NULL,   0.00, 'Active rental'),
    (8, '2026-02-22 11:00', NULL,                37500, NULL,   0.00, 'Active rental');

-- One payment per reservation. Cancelled reservations are refunded.
INSERT INTO Payment (reservation_id, amount, payment_date, method, status) VALUES
    (1,  180.00, '2025-05-25', 'credit_card',   'completed'),
    (2,  445.00, '2025-06-08', 'credit_card',   'completed'),
    (3,  447.00, '2025-06-13', 'debit_card',    'completed'),
    (4,  220.00, '2025-07-01', 'credit_card',   'completed'),
    (5,  190.00, '2025-07-18', 'credit_card',   'completed'),
    (6,   90.00, '2025-07-30', 'cash',          'completed'),
    (7,  234.00, '2026-02-19', 'credit_card',   'completed'),
    (8,  375.00, '2026-02-21', 'debit_card',    'completed'),
    (9,  700.00, '2026-02-25', 'credit_card',   'pending'),
    (10, 596.00, '2026-03-05', 'credit_card',   'pending'),
    (11, 475.00, '2025-09-10', 'credit_card',   'refunded'),
    (12, 267.00, '2026-03-15', 'bank_transfer', 'pending');

-- Vehicle 1 (Camry): last service at 21,000 mi, due again at 26,000. Now at 27,500 → OVERDUE.
-- Vehicle 7 (Malibu): last service at 27,000 mi, due again at 32,000. Now at 33,200 → OVERDUE.
INSERT INTO MaintenanceRecord (vehicle_id, service_date, service_type, cost, mileage_at_service, next_service_mileage, technician) VALUES
    (1,  '2025-01-15', 'Oil Change',              89.00, 21000, 26000,  'Joe Smith'),
    (2,  '2025-02-20', 'Tire Rotation',           45.00, 43000, 50000,  'Maria Lopez'),
    (3,  '2024-12-01', 'Brake Inspection',       120.00, 10000, 25000,  'Joe Smith'),
    (4,  '2025-03-10', 'Oil Change',              95.00, 16000, 21000,  'Carlos Ruiz'),
    (5,  '2025-04-05', 'Full Service',           350.00, 35000, 40000,  'Maria Lopez'),
    (6,  '2025-05-15', 'Transmission Service',   420.00, 50000,100000,  'Joe Smith'),
    (7,  '2024-11-20', 'Oil Change',              89.00, 27000, 32000,  'Carlos Ruiz'),
    (9,  '2025-06-01', 'Oil Change + Timing Belt',380.00,60000, 90000,  'Maria Lopez');

-- ============================================================
-- QUERIES
-- ============================================================

-- ------------------------------------------------------------
-- Q1: Which vehicles are available at Branch 1 (LAX) for
--     5–8 March 2026?
-- Relevance: Core booking query – staff quote customers or
--            confirm walk-in requests in real time.
-- Index used: idx_vehicle_branch_status (narrows Vehicle rows
--             to branch 1, non-retired/maintenance)
--             idx_reservation_vehicle_dates (overlap sub-query
--             jumps to each vehicle's reservation date slice)
-- ------------------------------------------------------------
SELECT 'Q1: Available vehicles at LAX for 2026-03-05 to 2026-03-08' AS query;

EXPLAIN QUERY PLAN
SELECT v.vehicle_id, v.make, v.model, v.year, v.category,
       v.daily_rate, v.license_plate
FROM   Vehicle v
WHERE  v.branch_id = 1
  AND  v.status NOT IN ('maintenance', 'retired')
  AND  v.vehicle_id NOT IN (
           -- Exclude any vehicle that has a confirmed or active reservation
           -- overlapping the requested window.
           -- Overlap condition: existing booking starts before our end
           --                    AND existing booking ends after our start.
           SELECT vehicle_id
           FROM   Reservation
           WHERE  status IN ('confirmed', 'active')
             AND  start_date < '2026-03-08'
             AND  end_date   > '2026-03-05'
       );

SELECT v.vehicle_id, v.make, v.model, v.year, v.category,
       v.daily_rate, v.license_plate
FROM   Vehicle v
WHERE  v.branch_id = 1
  AND  v.status NOT IN ('maintenance', 'retired')
  AND  v.vehicle_id NOT IN (
           SELECT vehicle_id
           FROM   Reservation
           WHERE  status IN ('confirmed', 'active')
             AND  start_date < '2026-03-08'
             AND  end_date   > '2026-03-05'
       );

-- ------------------------------------------------------------
-- Q2: Total revenue per branch for the full year 2025.
-- Relevance: Management financial reporting; identifies which
--            locations drive the most income.
-- Index used: idx_reservation_branch_date filters reservations
--             by branch then date in one B-tree seek.
--             idx_payment_reservation accelerates the JOIN.
-- ------------------------------------------------------------
SELECT 'Q2: Revenue per branch, year 2025' AS query;

EXPLAIN QUERY PLAN
SELECT   b.name        AS branch,
         b.city,
         COUNT(*)      AS rentals,
         SUM(p.amount) AS total_revenue
FROM     Payment p
JOIN     Reservation r ON p.reservation_id = r.reservation_id
JOIN     Branch      b ON r.pickup_branch  = b.branch_id
WHERE    r.start_date >= '2025-01-01'
  AND    r.start_date <  '2026-01-01'
  AND    r.status     != 'cancelled'
  AND    p.status      = 'completed'
GROUP BY b.branch_id, b.name, b.city
ORDER BY total_revenue DESC;

SELECT   b.name        AS branch,
         b.city,
         COUNT(*)      AS rentals,
         SUM(p.amount) AS total_revenue
FROM     Payment p
JOIN     Reservation r ON p.reservation_id = r.reservation_id
JOIN     Branch      b ON r.pickup_branch  = b.branch_id
WHERE    r.start_date >= '2025-01-01'
  AND    r.start_date <  '2026-01-01'
  AND    r.status     != 'cancelled'
  AND    p.status      = 'completed'
GROUP BY b.branch_id, b.name, b.city
ORDER BY total_revenue DESC;

-- ------------------------------------------------------------
-- Q3: Which vehicles are overdue for maintenance?
-- Relevance: Fleet managers need proactive alerts to pull cars
--            before mechanical failure or failed inspections.
-- Index used: idx_maintenance_vehicle_date lets the sub-query
--             find the most recent record per vehicle via
--             ORDER BY service_date DESC LIMIT 1 efficiently.
-- ------------------------------------------------------------
SELECT 'Q3: Vehicles overdue for maintenance' AS query;

EXPLAIN QUERY PLAN
SELECT v.vehicle_id,
       v.make, v.model, v.year, v.license_plate,
       v.current_mileage,
       m.next_service_mileage,
       m.service_type        AS last_service_type,
       m.service_date        AS last_service_date,
       (v.current_mileage - m.next_service_mileage) AS miles_overdue
FROM   Vehicle v
JOIN   MaintenanceRecord m ON m.vehicle_id = v.vehicle_id
WHERE  m.record_id = (
           -- Most recent maintenance record for this vehicle.
           SELECT record_id
           FROM   MaintenanceRecord
           WHERE  vehicle_id = v.vehicle_id
           ORDER  BY service_date DESC
           LIMIT  1
       )
  AND  v.current_mileage >= m.next_service_mileage
ORDER  BY miles_overdue DESC;

SELECT v.vehicle_id,
       v.make, v.model, v.year, v.license_plate,
       v.current_mileage,
       m.next_service_mileage,
       m.service_type        AS last_service_type,
       m.service_date        AS last_service_date,
       (v.current_mileage - m.next_service_mileage) AS miles_overdue
FROM   Vehicle v
JOIN   MaintenanceRecord m ON m.vehicle_id = v.vehicle_id
WHERE  m.record_id = (
           SELECT record_id
           FROM   MaintenanceRecord
           WHERE  vehicle_id = v.vehicle_id
           ORDER  BY service_date DESC
           LIMIT  1
       )
  AND  v.current_mileage >= m.next_service_mileage
ORDER  BY miles_overdue DESC;

-- ------------------------------------------------------------
-- Q4: Full rental history for Customer 1 (Alice Johnson).
-- Relevance: Customer service reps need this when handling
--            disputes, applying loyalty rewards, or verifying
--            past damage claims.
-- Index used: idx_reservation_customer jumps directly to
--             Alice's reservations.
--             idx_payment_reservation accelerates the JOIN.
-- ------------------------------------------------------------
SELECT 'Q4: Rental history for Customer 1 (Alice Johnson)' AS query;

EXPLAIN QUERY PLAN
SELECT  r.reservation_id,
        v.make, v.model, v.category,
        r.start_date, r.end_date, r.status,
        r.total_cost,
        COALESCE(rn.extra_charges, 0) AS extra_charges,
        p.method                      AS payment_method,
        p.status                      AS payment_status
FROM    Reservation r
JOIN    Vehicle     v  ON v.vehicle_id     = r.vehicle_id
LEFT JOIN Rental    rn ON rn.reservation_id = r.reservation_id
LEFT JOIN Payment   p  ON p.reservation_id  = r.reservation_id
WHERE   r.customer_id = 1
ORDER   BY r.start_date DESC;

SELECT  r.reservation_id,
        v.make, v.model, v.category,
        r.start_date, r.end_date, r.status,
        r.total_cost,
        COALESCE(rn.extra_charges, 0) AS extra_charges,
        p.method                      AS payment_method,
        p.status                      AS payment_status
FROM    Reservation r
JOIN    Vehicle     v  ON v.vehicle_id      = r.vehicle_id
LEFT JOIN Rental    rn ON rn.reservation_id = r.reservation_id
LEFT JOIN Payment   p  ON p.reservation_id  = r.reservation_id
WHERE   r.customer_id = 1
ORDER   BY r.start_date DESC;

-- ------------------------------------------------------------
-- Q5: Which vehicle category is most popular (by reservation
--     count) and what is the average rental cost per category?
-- Relevance: Fleet planning – which segment to expand when
--            ordering new vehicles.
-- No per-row index needed; this is an aggregation across the
-- full (non-cancelled) reservation set.
-- ------------------------------------------------------------
SELECT 'Q5: Popularity and avg revenue by vehicle category' AS query;

SELECT   v.category,
         COUNT(*)                       AS total_reservations,
         ROUND(AVG(r.total_cost), 2)   AS avg_rental_cost,
         ROUND(SUM(r.total_cost), 2)   AS total_revenue
FROM     Reservation r
JOIN     Vehicle     v ON v.vehicle_id = r.vehicle_id
WHERE    r.status != 'cancelled'
GROUP BY v.category
ORDER BY total_reservations DESC, total_revenue DESC;
