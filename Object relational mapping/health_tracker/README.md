# Patient Health Record & Medical History Tracker

A SQLite-backed database for storing and querying patient health data across a medical practice. It captures patient demographics, doctor profiles, visit history, diagnoses, prescriptions, lab results, and vaccination records. The system supports continuity of care (any doctor can review a patient's full history), safety checks (active prescriptions visible before new ones are written), and preventive care follow-ups (overdue boosters, abnormal lab flags).

---

## Tables

| Table | Purpose |
|-------|---------|
| `patients` | Core demographic record — name, date of birth, gender, blood type, known allergies, contact details, and an emergency contact. Allergies are stored here because they must be visible before any prescription is written. |
| `doctors` | Profile of each clinician — name, medical specialization, unique license number, and contact phone. The license number is kept `UNIQUE` to prevent accidental duplicate doctor records. |
| `appointments` | Links a patient to a doctor at a scheduled date and time. Stores duration, status (scheduled / completed / cancelled), and the patient's stated reason for visiting. Used for scheduling and confirming which visits were attended. |
| `medical_records` | Created for every completed visit. Records the visit date, attending doctor, diagnosis, treatment plan, and clinical notes. This is the primary source for a patient's longitudinal medical history. |
| `prescriptions` | Each row is one medication linked to a specific `medical_record` visit. Stores dosage, frequency, start/end dates, and an `is_active` flag so current medications can be quickly separated from historical ones. |
| `lab_results` | Stores individual test outcomes ordered by a doctor for a patient — result value, unit, normal range, and an `is_abnormal` flag. The flag allows quick dashboards of at-risk patients without parsing text ranges. |
| `vaccinations` | Records each vaccine administered to a patient, the date given, and the `next_due_date` for a booster. When `next_due_date` is in the past the patient is overdue for a follow-up. |

---

## Schema Diagram

```
PATIENT HEALTH RECORD TRACKER — SCHEMA DIAGRAM
===============================================

  Outer left  |  = patients ──1:N──> lab_results
  Outer right |  = doctors  ──1:N──> lab_results

     +----------------------+           +------------------+  
     | patients             |           | doctors          |  
     +----------------------+           +------------------+ _
  _  | patient_id        PK |           | doctor_id     PK |  |
  |  | first_name           |           | first_name       |  |
  |  | last_name            |           | last_name        |  |
  |  | date_of_birth        |           | specialization   |  |
  |  | gender               |           | license_number   |  |
  |  | blood_type           |           | phone            |  |
  |  | allergies            |           +---+----------+---+  |
  |  | phone                |               |          |      |
  |  | emergency_contact    |               |          |      |
  |  +--+-------+------+----+               |          |      |
  |     |       |      |                    |          |      |
  | 1:N |  1:N  |  1:N | 1:N           1:N  |     1:N  |      |
  |     |       |      |                    |          |      |
  | +---v---+   |  +---v--------------------v---+      |      |
  | |vaccin-|   |  |       appointments         |      |      |
  | |ations |   |  +----------------------------+      |      |
  | +-------+   |  | appointment_id          PK |      |      |
  | |vacc_id|   |  | patient_id   FK            |      |      |
  | |PK     |   |  | doctor_id    FK            |      |      |
  | |pat_id |   |  | scheduled_at               |      |      |
  | |FK     |   |  | duration_mins              |      |      |
  | |vacc_  |   |  | status                     |      |      |
  | |name   |   |  | reason                     |      |      |
  | |adm_at |   |  +----------------------------+      |      |
  | |nxt_due|   |                                      |      |
  | +-------+   +----v---------------------------------v+      |
  |             |          medical_records               |     |
  |             +-----------------------------------------+    |
  |             | record_id              PK               |    |
  |             | patient_id    FK                        |    |
  |             | doctor_id     FK                        |    |
  |             | visit_date                              |    |
  |             | diagnosis                               |    |
  |             | treatment                               |    |
  |             | notes                                   |    |
  |             +--------------------+--------------------+    |
  |                                  |                         |
  |                                  | 1:N                     |
  |                                  |                         |
  |             +--------------------v--------------------+    |
  |             |            prescriptions                |    |
  |             +-----------------------------------------+    |
  |             | prescription_id        PK               |    |
  |             | record_id    FK                         |    |
  |             | medication_name                         |    |
  |             | dosage                                  |    |
  |             | frequency                               |    |
  |             | start_date                              |    |
  |             | end_date                                |    |
  |             | is_active                               |    |
  |             +-----------------------------------------+    |
  |                                                            |
  +v----------------------------------------------------------v+
  |                      lab_results                           |
  +------------------------------------------------------------+
  | result_id        PK                                        |
  | patient_id       FK -> patients                            |
  | doctor_id        FK -> doctors                             |
  | test_name                                                  |
  | test_date                                                  |
  | result_value                                               |
  | unit                                                       |
  | normal_range                                               |
  | is_abnormal                                                |
  +------------------------------------------------------------+
```

