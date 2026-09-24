-- ============================================================
-- Patient Health Record & Medical History Tracker -- Mock Data
-- ============================================================

PRAGMA foreign_keys = ON;

-- ── Patients ─────────────────────────────────────────────────
INSERT INTO patients (first_name, last_name, date_of_birth, gender, blood_type, allergies, phone, emergency_contact_name, emergency_contact_phone) VALUES
    ('James',    'Walker',   '1975-04-12', 'Male',   'A+',  'Penicillin',          '555-1001', 'Mary Walker',    '555-1002'),
    ('Susan',    'Hall',     '1988-09-23', 'Female', 'O-',  NULL,                  '555-1003', 'Tom Hall',       '555-1004'),
    ('Carlos',   'Ramirez',  '1963-01-30', 'Male',   'B+',  'Sulfa drugs, Aspirin','555-1005', 'Rosa Ramirez',   '555-1006'),
    ('Emily',    'Zhang',    '1995-06-14', 'Female', 'AB+', NULL,                  '555-1007', 'Wei Zhang',      '555-1008'),
    ('Michael',  'Turner',   '1950-11-05', 'Male',   'O+',  'Latex',               '555-1009', 'Linda Turner',   '555-1010'),
    ('Priya',    'Nair',     '1982-03-19', 'Female', 'A-',  'Codeine',             '555-1011', 'Raj Nair',       '555-1012'),
    ('Thomas',   'Berg',     '2000-08-07', 'Male',   'B-',  NULL,                  '555-1013', 'Anna Berg',      '555-1014'),
    ('Fatima',   'Hassan',   '1971-12-25', 'Female', 'O+',  'Ibuprofen',           '555-1015', 'Yusuf Hassan',   '555-1016');

-- ── Doctors ──────────────────────────────────────────────────
INSERT INTO doctors (first_name, last_name, specialization, license_number, phone) VALUES
    ('Dr. Olivia', 'Park',    'General Practice',  'LIC-10011', '555-2001'),
    ('Dr. Nathan', 'Brooks',  'Cardiology',        'LIC-10022', '555-2002'),
    ('Dr. Sara',   'Mendez',  'Endocrinology',     'LIC-10033', '555-2003'),
    ('Dr. Ahmed',  'Farouk',  'Orthopedics',       'LIC-10044', '555-2004'),
    ('Dr. Claire', 'Wilson',  'Neurology',         'LIC-10055', '555-2005');

-- ── Appointments ─────────────────────────────────────────────
INSERT INTO appointments (patient_id, doctor_id, scheduled_at, duration_minutes, status, reason) VALUES
    (1, 1, '2025-10-05 09:00', 30, 'completed',  'Annual check-up'),
    (1, 2, '2026-01-15 10:30', 45, 'completed',  'Chest pain follow-up'),
    (2, 1, '2025-11-20 11:00', 30, 'completed',  'Flu symptoms'),
    (3, 3, '2025-09-10 14:00', 60, 'completed',  'Diabetes management review'),
    (3, 1, '2026-02-10 09:30', 30, 'completed',  'Blood pressure check'),
    (4, 1, '2026-01-08 08:00', 30, 'completed',  'Routine wellness visit'),
    (5, 2, '2025-12-03 13:00', 45, 'completed',  'Hypertension review'),
    (5, 5, '2026-02-20 15:00', 60, 'scheduled',  'Headache evaluation'),
    (6, 3, '2026-01-22 10:00', 45, 'completed',  'Thyroid levels check'),
    (7, 4, '2026-02-01 11:00', 30, 'completed',  'Knee pain'),
    (8, 1, '2026-02-15 09:00', 30, 'completed',  'Routine check-up'),
    (1, 2, '2026-03-01 10:00', 45, 'scheduled',  'Cardiology follow-up'),
    (3, 3, '2026-03-15 14:00', 60, 'scheduled',  'Quarterly diabetes review');

-- ── Medical Records ──────────────────────────────────────────
INSERT INTO medical_records (patient_id, doctor_id, visit_date, diagnosis, treatment, notes) VALUES
    (1, 1, '2025-10-05', 'Hypertension Stage 1',            'Lifestyle changes, monitoring',         'BP: 145/92. Advised low-sodium diet and exercise'),
    (1, 2, '2026-01-15', 'Stable Angina',                   'Beta-blockers, aspirin therapy',        'ECG shows mild ischemic changes'),
    (2, 1, '2025-11-20', 'Influenza A',                     'Rest, fluids, antiviral medication',    'High fever 39.2C, rapid flu test positive'),
    (3, 3, '2025-09-10', 'Type 2 Diabetes (uncontrolled)',  'Metformin dose increase, diet plan',    'HbA1c at 8.9%, referred to nutritionist'),
    (3, 1, '2026-02-10', 'Hypertension + Diabetes',         'ACE inhibitor added',                   'BP: 152/96. Metformin ongoing'),
    (4, 1, '2026-01-08', 'No acute concerns',               'Routine screening labs ordered',        'Patient reports mild fatigue'),
    (5, 2, '2025-12-03', 'Essential Hypertension',          'Amlodipine 5mg daily',                  'BP: 165/100. ECG normal'),
    (6, 3, '2026-01-22', 'Hypothyroidism',                  'Levothyroxine 50mcg daily',             'TSH elevated at 7.2 mIU/L'),
    (7, 4, '2026-02-01', 'Patellofemoral Pain Syndrome',    'Physiotherapy, NSAIDs as needed',       'X-ray clear, no structural damage'),
    (8, 1, '2026-02-15', 'Iron Deficiency Anaemia',         'Ferrous sulfate 200mg daily',           'Hb: 9.8 g/dL, ferritin low');

-- ── Prescriptions ────────────────────────────────────────────
-- Linked to medical_records (record_id 1-10)
INSERT INTO prescriptions (record_id, medication_name, dosage, frequency, start_date, end_date, is_active) VALUES
    -- Record 1: James - Hypertension
    (1, 'Ramipril',      '5mg',   'Once daily',    '2025-10-05', NULL,         1),
    -- Record 2: James - Stable Angina
    (2, 'Metoprolol',    '25mg',  'Twice daily',   '2026-01-15', NULL,         1),
    (2, 'Aspirin',       '75mg',  'Once daily',    '2026-01-15', NULL,         1),
    -- Record 3: Susan - Influenza
    (3, 'Oseltamivir',   '75mg',  'Twice daily',   '2025-11-20', '2025-11-25', 0),
    -- Record 4: Carlos - Diabetes
    (4, 'Metformin',     '1000mg','Twice daily',   '2025-09-10', NULL,         1),
    -- Record 5: Carlos - Hypertension added
    (5, 'Lisinopril',    '10mg',  'Once daily',    '2026-02-10', NULL,         1),
    -- Record 7: Michael - Hypertension
    (7, 'Amlodipine',    '5mg',   'Once daily',    '2025-12-03', NULL,         1),
    -- Record 8: Priya - Hypothyroidism
    (8, 'Levothyroxine', '50mcg', 'Once daily (morning)', '2026-01-22', NULL,  1),
    -- Record 10: Fatima - Anaemia
    (10,'Ferrous Sulfate','200mg','Once daily with food', '2026-02-15', '2026-05-15', 1);

-- ── Lab Results ──────────────────────────────────────────────
INSERT INTO lab_results (patient_id, doctor_id, test_name, test_date, result_value, unit, normal_range, is_abnormal) VALUES
    -- James (1): blood work after cardiology visit
    (1, 2, 'LDL Cholesterol',   '2026-01-15', '148',  'mg/dL', '< 100',     1),
    (1, 2, 'HDL Cholesterol',   '2026-01-15', '42',   'mg/dL', '> 40',      0),
    (1, 2, 'Blood Pressure',    '2026-01-15', '148/94','mmHg', '< 130/80',  1),
    -- Carlos (3): diabetes management
    (3, 3, 'HbA1c',             '2025-09-10', '8.9',  '%',     '< 7.0',     1),
    (3, 3, 'Fasting Glucose',   '2025-09-10', '187',  'mg/dL', '70-100',    1),
    (3, 1, 'HbA1c',             '2026-02-10', '8.2',  '%',     '< 7.0',     1),
    (3, 1, 'Blood Pressure',    '2026-02-10', '152/96','mmHg', '< 130/80',  1),
    -- Emily (4): routine labs
    (4, 1, 'Complete Blood Count','2026-01-08','Normal','',    'Normal',     0),
    (4, 1, 'Fasting Glucose',   '2026-01-08', '88',   'mg/dL', '70-100',    0),
    -- Michael (5): cardiology
    (5, 2, 'Blood Pressure',    '2025-12-03', '165/100','mmHg','< 130/80',  1),
    (5, 2, 'Creatinine',        '2025-12-03', '1.1',  'mg/dL', '0.7-1.2',   0),
    -- Priya (6): thyroid
    (6, 3, 'TSH',               '2026-01-22', '7.2',  'mIU/L', '0.5-4.5',   1),
    (6, 3, 'Free T4',           '2026-01-22', '0.7',  'ng/dL', '0.8-1.8',   1),
    -- Fatima (8): anaemia workup
    (8, 1, 'Haemoglobin',       '2026-02-15', '9.8',  'g/dL',  '12.0-16.0', 1),
    (8, 1, 'Ferritin',          '2026-02-15', '5',    'ng/mL', '12-150',    1);

-- ── Vaccinations ─────────────────────────────────────────────
INSERT INTO vaccinations (patient_id, vaccine_name, administered_at, next_due_date, administered_by) VALUES
    (1, 'Influenza',         '2025-10-05', '2026-10-05', 'Dr. Olivia Park'),
    (1, 'Tetanus (Td)',      '2022-03-10', '2032-03-10', 'Dr. Olivia Park'),
    (2, 'COVID-19 Booster',  '2025-09-15', '2026-09-15', 'Dr. Olivia Park'),
    (2, 'Influenza',         '2025-09-15', '2026-09-15', 'Dr. Olivia Park'),
    (3, 'Influenza',         '2024-10-20', '2025-10-20', 'Dr. Olivia Park'),   -- overdue
    (3, 'Pneumococcal',      '2023-01-15', NULL,          'Dr. Sara Mendez'),
    (4, 'HPV',               '2025-06-01', '2025-12-01', 'Dr. Olivia Park'),   -- overdue booster
    (5, 'Influenza',         '2025-11-10', '2026-11-10', 'Dr. Nathan Brooks'),
    (5, 'Shingles (Shingrix)','2024-06-20','2025-06-20', 'Dr. Nathan Brooks'), -- overdue 2nd dose
    (6, 'COVID-19 Booster',  '2025-11-22', '2026-11-22', 'Dr. Sara Mendez'),
    (7, 'Tetanus (Td)',      '2021-08-07', '2031-08-07', 'Dr. Ahmed Farouk'),
    (8, 'Influenza',         '2025-10-30', '2026-10-30', 'Dr. Olivia Park');
