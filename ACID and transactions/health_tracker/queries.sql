-- ============================================================
-- Patient Health Record & Medical History Tracker -- Queries
-- ============================================================

PRAGMA foreign_keys = ON;

-- ────────────────────────────────────────────────────────────
-- QUESTION 1
-- "What are all active prescriptions for a specific patient?"
--
-- WHY: Before prescribing any new medication a doctor must
-- see what the patient is already taking to avoid dangerous
-- drug interactions.  This is arguably the most safety-critical
-- query in the system.
-- ────────────────────────────────────────────────────────────
SELECT
    p.medication_name,
    p.dosage,
    p.frequency,
    p.start_date,
    p.end_date,
    mr.diagnosis,
    d.first_name || ' ' || d.last_name AS prescribed_by
FROM prescriptions  p
JOIN medical_records mr ON p.record_id  = mr.record_id
JOIN doctors         d  ON mr.doctor_id = d.doctor_id
WHERE mr.patient_id = 1    -- change to any patient_id
  AND p.is_active   = 1
ORDER BY p.start_date DESC;


-- ────────────────────────────────────────────────────────────
-- QUESTION 2
-- "What is a patient's complete visit history — date, doctor,
--  diagnosis, and treatment?"
--
-- WHY: Continuity of care depends on any new doctor quickly
-- understanding the patient's full medical background.  This
-- is the definitive "medical history" report.
-- ────────────────────────────────────────────────────────────
SELECT
    mr.visit_date,
    d.first_name || ' ' || d.last_name AS doctor,
    d.specialization,
    mr.diagnosis,
    mr.treatment,
    mr.notes
FROM medical_records mr
JOIN doctors         d ON mr.doctor_id = d.doctor_id
WHERE mr.patient_id = 3    -- change to any patient_id
ORDER BY mr.visit_date DESC;


-- ────────────────────────────────────────────────────────────
-- QUESTION 3
-- "Which patients have had at least one abnormal lab result?"
--
-- WHY: This is a proactive care dashboard for clinicians;
-- it surfaces at-risk patients who may need follow-up even
-- if they haven't scheduled an appointment.
-- ────────────────────────────────────────────────────────────
SELECT
    pa.first_name || ' ' || pa.last_name   AS patient,
    pa.date_of_birth,
    COUNT(lr.result_id)                    AS abnormal_results,
    MAX(lr.test_date)                      AS most_recent_abnormal,
    GROUP_CONCAT(DISTINCT lr.test_name)    AS tests_flagged
FROM lab_results lr
JOIN patients    pa ON lr.patient_id = pa.patient_id
WHERE lr.is_abnormal = 1
GROUP BY lr.patient_id
ORDER BY abnormal_results DESC;


-- ────────────────────────────────────────────────────────────
-- QUESTION 4
-- "What is a specific doctor's upcoming appointment schedule,
--  including patient names and visit reasons?"
--
-- WHY: A doctor's daily schedule view is essential for
-- clinical efficiency — allowing preparation, time management,
-- and ensuring no appointments are double-booked.
-- ────────────────────────────────────────────────────────────
SELECT
    a.scheduled_at,
    a.duration_minutes,
    pa.first_name || ' ' || pa.last_name  AS patient,
    pa.phone                               AS patient_phone,
    a.reason,
    a.status
FROM appointments a
JOIN patients     pa ON a.patient_id = pa.patient_id
WHERE a.doctor_id = 2           -- Dr. Nathan Brooks; change to any doctor_id
  AND a.status    = 'scheduled' -- only future/pending appointments
ORDER BY a.scheduled_at;


-- ============================================================
-- TRANSACTIONS
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- TRANSACTION 1 — Recording a doctor visit (medical record +
--                 prescriptions written in the same visit)
--
-- WHY we use a transaction here:
--   A visit record and its prescriptions are a single clinical
--   event.  If the medical_record insert succeeds but the
--   prescription inserts fail (e.g. due to a constraint or
--   application crash), the record would show a diagnosis with
--   no treatment — clinically dangerous and misleading.
--   A transaction guarantees both writes succeed together or
--   neither is persisted.
-- ────────────────────────────────────────────────────────────
BEGIN TRANSACTION;

-- Step 1: Create the medical record for the visit
INSERT INTO medical_records (patient_id, doctor_id, visit_date, diagnosis, treatment, notes)
VALUES (
    7,                  -- Thomas Berg
    4,                  -- Dr. Ahmed Farouk (Orthopedics)
    date('now'),
    'Patellofemoral Pain Syndrome - follow-up',
    'Continue physiotherapy; naproxen prescribed for pain management',
    'Swelling reduced since last visit. Patient reports 60% improvement.'
);

-- Step 2: Capture the auto-generated record_id from the insert above
-- (In a real application this would be done in application code,
--  e.g. using lastrowid.  Here we use a SQLite subquery.)

-- Step 3: Add the prescription linked to that new record
INSERT INTO prescriptions (record_id, medication_name, dosage, frequency, start_date, end_date, is_active)
VALUES (
    (SELECT MAX(record_id) FROM medical_records WHERE patient_id = 7),
    'Naproxen', '250mg', 'Twice daily with food', date('now'), date('now', '+30 days'), 1
);

COMMIT;


-- ────────────────────────────────────────────────────────────
-- TRANSACTION 2 — Recording a newly discovered allergy and
--                 immediately deactivating every conflicting
--                 active prescription
--
-- WHY we use a transaction here:
--   When a patient is found to be allergic to a drug they are
--   currently prescribed, two writes must happen together:
--     (a) add the allergen to the patient's allergy record, and
--     (b) deactivate every active prescription for that drug.
--   The two writes affect different tables (patients and
--   prescriptions) yet form a single clinical event.  Either
--   partial state is dangerous:
--     - Allergy saved but prescription still active →
--       pharmacy continues dispensing the harmful drug.
--     - Prescription deactivated but allergy not saved →
--       the next prescriber sees no warning and may
--       re-prescribe the same medication.
--   A transaction guarantees both writes succeed together
--   or neither is committed.
-- ────────────────────────────────────────────────────────────
BEGIN TRANSACTION;

-- Step 1: Add the allergen to the patient's allergy list.
-- COALESCE handles the case where allergies was previously NULL
-- (no known allergies) — it returns just the new value rather
-- than 'NULL, Aspirin'.
UPDATE patients
SET    allergies = COALESCE(allergies || ', ', '') || 'Aspirin'
WHERE  patient_id = 1;   -- James Walker

-- Step 2: Deactivate every active prescription for that drug
-- belonging to this patient.  Prescriptions only store record_id,
-- not patient_id directly, so we reach the patient through
-- medical_records using a subquery.
UPDATE prescriptions
SET    is_active = 0
WHERE  is_active = 1
  AND  LOWER(medication_name) LIKE '%aspirin%'
  AND  record_id IN (
           SELECT record_id
           FROM   medical_records
           WHERE  patient_id = 1
       );

COMMIT;
