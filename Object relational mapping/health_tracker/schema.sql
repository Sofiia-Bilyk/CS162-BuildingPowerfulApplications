-- ============================================================
-- Patient Health Record & Medical History Tracker -- Schema
-- ============================================================

-- Enable foreign key enforcement in SQLite
PRAGMA foreign_keys = ON;

-- Core patient demographics and emergency contact info
CREATE TABLE patients (
    patient_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name              TEXT    NOT NULL,
    last_name               TEXT    NOT NULL,
    date_of_birth           TEXT    NOT NULL,   -- stored as YYYY-MM-DD
    gender                  TEXT    NOT NULL CHECK(gender IN ('Male', 'Female', 'Other')),
    blood_type              TEXT,
    allergies               TEXT,               -- comma-separated list of known allergens
    phone                   TEXT,
    emergency_contact_name  TEXT,
    emergency_contact_phone TEXT
);

-- Doctors with their medical specialization and license
CREATE TABLE doctors (
    doctor_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name     TEXT    NOT NULL,
    last_name      TEXT    NOT NULL,
    specialization TEXT    NOT NULL,
    license_number TEXT    NOT NULL UNIQUE,
    phone          TEXT
);

-- Appointments link a patient to a doctor at a scheduled time
CREATE TABLE appointments (
    appointment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL,
    doctor_id        INTEGER NOT NULL,
    scheduled_at     TEXT    NOT NULL,          -- YYYY-MM-DD HH:MM
    duration_minutes INTEGER NOT NULL DEFAULT 30,
    status           TEXT    NOT NULL DEFAULT 'scheduled'
                             CHECK(status IN ('scheduled', 'completed', 'cancelled')),
    reason           TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)
);

-- A medical record is created for each completed visit; records diagnosis and treatment
CREATE TABLE medical_records (
    record_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id  INTEGER NOT NULL,
    visit_date TEXT    NOT NULL,
    diagnosis  TEXT,
    treatment  TEXT,
    notes      TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)
);

-- Each prescription belongs to a medical_record visit;
-- is_active = 1 means currently prescribed
CREATE TABLE prescriptions (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id       INTEGER NOT NULL,
    medication_name TEXT    NOT NULL,
    dosage          TEXT    NOT NULL,
    frequency       TEXT    NOT NULL,
    start_date      TEXT    NOT NULL,
    end_date        TEXT,               -- NULL means open-ended (ongoing)
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id)
);

-- Lab results store individual test outcomes; is_abnormal flags out-of-range values
CREATE TABLE lab_results (
    result_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id   INTEGER NOT NULL,
    doctor_id    INTEGER NOT NULL,
    test_name    TEXT    NOT NULL,
    test_date    TEXT    NOT NULL,
    result_value TEXT    NOT NULL,
    unit         TEXT,
    normal_range TEXT,
    is_abnormal  INTEGER NOT NULL DEFAULT 0 CHECK(is_abnormal IN (0, 1)),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)
);

-- Vaccination history and upcoming booster schedule
CREATE TABLE vaccinations (
    vaccination_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      INTEGER NOT NULL,
    vaccine_name    TEXT    NOT NULL,
    administered_at TEXT    NOT NULL,   -- YYYY-MM-DD
    next_due_date   TEXT,               -- NULL if no booster is required
    administered_by TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);
