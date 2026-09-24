# Patient Health Record & Medical History Tracker — SQLAlchemy Implementation

from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey,
    func, distinct, literal
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()


# ── Models ────────────────────────────────────────────────────────────────────

class Patient(Base):
    __tablename__ = 'patients'
    patient_id              = Column(Integer, primary_key=True, autoincrement=True)
    first_name              = Column(String, nullable=False)
    last_name               = Column(String, nullable=False)
    date_of_birth           = Column(String, nullable=False)
    gender                  = Column(String, nullable=False)
    blood_type              = Column(String)
    allergies               = Column(String)
    phone                   = Column(String)
    emergency_contact_name  = Column(String)
    emergency_contact_phone = Column(String)

    def __repr__(self):
        return f"<Patient({self.patient_id}: {self.first_name} {self.last_name})>"


class Doctor(Base):
    __tablename__ = 'doctors'
    doctor_id      = Column(Integer, primary_key=True, autoincrement=True)
    first_name     = Column(String, nullable=False)
    last_name      = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    license_number = Column(String, nullable=False, unique=True)
    phone          = Column(String)

    def __repr__(self):
        return f"<Doctor({self.doctor_id}: {self.first_name} {self.last_name})>"


class Appointment(Base):
    __tablename__ = 'appointments'
    appointment_id   = Column(Integer, primary_key=True, autoincrement=True)
    patient_id       = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    doctor_id        = Column(Integer, ForeignKey('doctors.doctor_id'),   nullable=False)
    scheduled_at     = Column(String,  nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=30)
    status           = Column(String,  nullable=False, default='scheduled')
    reason           = Column(String)


class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    record_id  = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    doctor_id  = Column(Integer, ForeignKey('doctors.doctor_id'),   nullable=False)
    visit_date = Column(String,  nullable=False)
    diagnosis  = Column(String)
    treatment  = Column(String)
    notes      = Column(String)


class Prescription(Base):
    __tablename__ = 'prescriptions'
    prescription_id = Column(Integer, primary_key=True, autoincrement=True)
    record_id       = Column(Integer, ForeignKey('medical_records.record_id'), nullable=False)
    medication_name = Column(String,  nullable=False)
    dosage          = Column(String,  nullable=False)
    frequency       = Column(String,  nullable=False)
    start_date      = Column(String,  nullable=False)
    end_date        = Column(String)
    is_active       = Column(Integer, nullable=False, default=1)


class LabResult(Base):
    __tablename__ = 'lab_results'
    result_id    = Column(Integer, primary_key=True, autoincrement=True)
    patient_id   = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    doctor_id    = Column(Integer, ForeignKey('doctors.doctor_id'),   nullable=False)
    test_name    = Column(String,  nullable=False)
    test_date    = Column(String,  nullable=False)
    result_value = Column(String,  nullable=False)
    unit         = Column(String)
    normal_range = Column(String)
    is_abnormal  = Column(Integer, nullable=False, default=0)


class Vaccination(Base):
    __tablename__ = 'vaccinations'
    vaccination_id  = Column(Integer, primary_key=True, autoincrement=True)
    patient_id      = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    vaccine_name    = Column(String,  nullable=False)
    administered_at = Column(String,  nullable=False)
    next_due_date   = Column(String)
    administered_by = Column(String)


# ── Create tables & session ───────────────────────────────────────────────────

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# ── Insert data ───────────────────────────────────────────────────────────────

session.add_all([
    Patient(first_name='James',   last_name='Walker',  date_of_birth='1975-04-12', gender='Male',   blood_type='A+',  allergies='Penicillin',          phone='555-1001', emergency_contact_name='Mary Walker',  emergency_contact_phone='555-1002'),
    Patient(first_name='Susan',   last_name='Hall',    date_of_birth='1988-09-23', gender='Female', blood_type='O-',  allergies=None,                   phone='555-1003', emergency_contact_name='Tom Hall',     emergency_contact_phone='555-1004'),
    Patient(first_name='Carlos',  last_name='Ramirez', date_of_birth='1963-01-30', gender='Male',   blood_type='B+',  allergies='Sulfa drugs, Aspirin', phone='555-1005', emergency_contact_name='Rosa Ramirez', emergency_contact_phone='555-1006'),
    Patient(first_name='Emily',   last_name='Zhang',   date_of_birth='1995-06-14', gender='Female', blood_type='AB+', allergies=None,                   phone='555-1007', emergency_contact_name='Wei Zhang',    emergency_contact_phone='555-1008'),
    Patient(first_name='Michael', last_name='Turner',  date_of_birth='1950-11-05', gender='Male',   blood_type='O+',  allergies='Latex',                phone='555-1009', emergency_contact_name='Linda Turner', emergency_contact_phone='555-1010'),
    Patient(first_name='Priya',   last_name='Nair',    date_of_birth='1982-03-19', gender='Female', blood_type='A-',  allergies='Codeine',              phone='555-1011', emergency_contact_name='Raj Nair',     emergency_contact_phone='555-1012'),
    Patient(first_name='Thomas',  last_name='Berg',    date_of_birth='2000-08-07', gender='Male',   blood_type='B-',  allergies=None,                   phone='555-1013', emergency_contact_name='Anna Berg',    emergency_contact_phone='555-1014'),
    Patient(first_name='Fatima',  last_name='Hassan',  date_of_birth='1971-12-25', gender='Female', blood_type='O+',  allergies='Ibuprofen',            phone='555-1015', emergency_contact_name='Yusuf Hassan', emergency_contact_phone='555-1016'),
])

session.add_all([
    Doctor(first_name='Dr. Olivia', last_name='Park',   specialization='General Practice', license_number='LIC-10011', phone='555-2001'),
    Doctor(first_name='Dr. Nathan', last_name='Brooks', specialization='Cardiology',       license_number='LIC-10022', phone='555-2002'),
    Doctor(first_name='Dr. Sara',   last_name='Mendez', specialization='Endocrinology',    license_number='LIC-10033', phone='555-2003'),
    Doctor(first_name='Dr. Ahmed',  last_name='Farouk', specialization='Orthopedics',      license_number='LIC-10044', phone='555-2004'),
    Doctor(first_name='Dr. Claire', last_name='Wilson', specialization='Neurology',        license_number='LIC-10055', phone='555-2005'),
])
session.commit()

session.add_all([
    Appointment(patient_id=1, doctor_id=1, scheduled_at='2025-10-05 09:00', duration_minutes=30, status='completed', reason='Annual check-up'),
    Appointment(patient_id=1, doctor_id=2, scheduled_at='2026-01-15 10:30', duration_minutes=45, status='completed', reason='Chest pain follow-up'),
    Appointment(patient_id=2, doctor_id=1, scheduled_at='2025-11-20 11:00', duration_minutes=30, status='completed', reason='Flu symptoms'),
    Appointment(patient_id=3, doctor_id=3, scheduled_at='2025-09-10 14:00', duration_minutes=60, status='completed', reason='Diabetes management review'),
    Appointment(patient_id=3, doctor_id=1, scheduled_at='2026-02-10 09:30', duration_minutes=30, status='completed', reason='Blood pressure check'),
    Appointment(patient_id=4, doctor_id=1, scheduled_at='2026-01-08 08:00', duration_minutes=30, status='completed', reason='Routine wellness visit'),
    Appointment(patient_id=5, doctor_id=2, scheduled_at='2025-12-03 13:00', duration_minutes=45, status='completed', reason='Hypertension review'),
    Appointment(patient_id=5, doctor_id=5, scheduled_at='2026-02-20 15:00', duration_minutes=60, status='scheduled', reason='Headache evaluation'),
    Appointment(patient_id=6, doctor_id=3, scheduled_at='2026-01-22 10:00', duration_minutes=45, status='completed', reason='Thyroid levels check'),
    Appointment(patient_id=7, doctor_id=4, scheduled_at='2026-02-01 11:00', duration_minutes=30, status='completed', reason='Knee pain'),
    Appointment(patient_id=8, doctor_id=1, scheduled_at='2026-02-15 09:00', duration_minutes=30, status='completed', reason='Routine check-up'),
    Appointment(patient_id=1, doctor_id=2, scheduled_at='2026-03-01 10:00', duration_minutes=45, status='scheduled', reason='Cardiology follow-up'),
    Appointment(patient_id=3, doctor_id=3, scheduled_at='2026-03-15 14:00', duration_minutes=60, status='scheduled', reason='Quarterly diabetes review'),
])

session.add_all([
    MedicalRecord(patient_id=1, doctor_id=1, visit_date='2025-10-05', diagnosis='Hypertension Stage 1',           treatment='Lifestyle changes, monitoring',        notes='BP: 145/92. Advised low-sodium diet and exercise'),
    MedicalRecord(patient_id=1, doctor_id=2, visit_date='2026-01-15', diagnosis='Stable Angina',                  treatment='Beta-blockers, aspirin therapy',        notes='ECG shows mild ischemic changes'),
    MedicalRecord(patient_id=2, doctor_id=1, visit_date='2025-11-20', diagnosis='Influenza A',                    treatment='Rest, fluids, antiviral medication',     notes='High fever 39.2C, rapid flu test positive'),
    MedicalRecord(patient_id=3, doctor_id=3, visit_date='2025-09-10', diagnosis='Type 2 Diabetes (uncontrolled)', treatment='Metformin dose increase, diet plan',     notes='HbA1c at 8.9%, referred to nutritionist'),
    MedicalRecord(patient_id=3, doctor_id=1, visit_date='2026-02-10', diagnosis='Hypertension + Diabetes',        treatment='ACE inhibitor added',                   notes='BP: 152/96. Metformin ongoing'),
    MedicalRecord(patient_id=4, doctor_id=1, visit_date='2026-01-08', diagnosis='No acute concerns',              treatment='Routine screening labs ordered',          notes='Patient reports mild fatigue'),
    MedicalRecord(patient_id=5, doctor_id=2, visit_date='2025-12-03', diagnosis='Essential Hypertension',         treatment='Amlodipine 5mg daily',                  notes='BP: 165/100. ECG normal'),
    MedicalRecord(patient_id=6, doctor_id=3, visit_date='2026-01-22', diagnosis='Hypothyroidism',                 treatment='Levothyroxine 50mcg daily',              notes='TSH elevated at 7.2 mIU/L'),
    MedicalRecord(patient_id=7, doctor_id=4, visit_date='2026-02-01', diagnosis='Patellofemoral Pain Syndrome',   treatment='Physiotherapy, NSAIDs as needed',        notes='X-ray clear, no structural damage'),
    MedicalRecord(patient_id=8, doctor_id=1, visit_date='2026-02-15', diagnosis='Iron Deficiency Anaemia',        treatment='Ferrous sulfate 200mg daily',            notes='Hb: 9.8 g/dL, ferritin low'),
])
session.commit()

session.add_all([
    Prescription(record_id=1,  medication_name='Ramipril',        dosage='5mg',    frequency='Once daily',           start_date='2025-10-05', end_date=None,         is_active=1),
    Prescription(record_id=2,  medication_name='Metoprolol',      dosage='25mg',   frequency='Twice daily',          start_date='2026-01-15', end_date=None,         is_active=1),
    Prescription(record_id=2,  medication_name='Aspirin',         dosage='75mg',   frequency='Once daily',           start_date='2026-01-15', end_date=None,         is_active=1),
    Prescription(record_id=3,  medication_name='Oseltamivir',     dosage='75mg',   frequency='Twice daily',          start_date='2025-11-20', end_date='2025-11-25', is_active=0),
    Prescription(record_id=4,  medication_name='Metformin',       dosage='1000mg', frequency='Twice daily',          start_date='2025-09-10', end_date=None,         is_active=1),
    Prescription(record_id=5,  medication_name='Lisinopril',      dosage='10mg',   frequency='Once daily',           start_date='2026-02-10', end_date=None,         is_active=1),
    Prescription(record_id=7,  medication_name='Amlodipine',      dosage='5mg',    frequency='Once daily',           start_date='2025-12-03', end_date=None,         is_active=1),
    Prescription(record_id=8,  medication_name='Levothyroxine',   dosage='50mcg',  frequency='Once daily (morning)', start_date='2026-01-22', end_date=None,         is_active=1),
    Prescription(record_id=10, medication_name='Ferrous Sulfate', dosage='200mg',  frequency='Once daily with food', start_date='2026-02-15', end_date='2026-05-15', is_active=1),
])

session.add_all([
    LabResult(patient_id=1, doctor_id=2, test_name='LDL Cholesterol',     test_date='2026-01-15', result_value='148',     unit='mg/dL', normal_range='< 100',    is_abnormal=1),
    LabResult(patient_id=1, doctor_id=2, test_name='HDL Cholesterol',     test_date='2026-01-15', result_value='42',      unit='mg/dL', normal_range='> 40',     is_abnormal=0),
    LabResult(patient_id=1, doctor_id=2, test_name='Blood Pressure',      test_date='2026-01-15', result_value='148/94',  unit='mmHg',  normal_range='< 130/80', is_abnormal=1),
    LabResult(patient_id=3, doctor_id=3, test_name='HbA1c',               test_date='2025-09-10', result_value='8.9',     unit='%',     normal_range='< 7.0',    is_abnormal=1),
    LabResult(patient_id=3, doctor_id=3, test_name='Fasting Glucose',     test_date='2025-09-10', result_value='187',     unit='mg/dL', normal_range='70-100',   is_abnormal=1),
    LabResult(patient_id=3, doctor_id=1, test_name='HbA1c',               test_date='2026-02-10', result_value='8.2',     unit='%',     normal_range='< 7.0',    is_abnormal=1),
    LabResult(patient_id=3, doctor_id=1, test_name='Blood Pressure',      test_date='2026-02-10', result_value='152/96',  unit='mmHg',  normal_range='< 130/80', is_abnormal=1),
    LabResult(patient_id=4, doctor_id=1, test_name='Complete Blood Count', test_date='2026-01-08', result_value='Normal', unit='',      normal_range='Normal',   is_abnormal=0),
    LabResult(patient_id=4, doctor_id=1, test_name='Fasting Glucose',     test_date='2026-01-08', result_value='88',      unit='mg/dL', normal_range='70-100',   is_abnormal=0),
    LabResult(patient_id=5, doctor_id=2, test_name='Blood Pressure',      test_date='2025-12-03', result_value='165/100', unit='mmHg',  normal_range='< 130/80', is_abnormal=1),
    LabResult(patient_id=5, doctor_id=2, test_name='Creatinine',          test_date='2025-12-03', result_value='1.1',     unit='mg/dL', normal_range='0.7-1.2',  is_abnormal=0),
    LabResult(patient_id=6, doctor_id=3, test_name='TSH',                 test_date='2026-01-22', result_value='7.2',     unit='mIU/L', normal_range='0.5-4.5',  is_abnormal=1),
    LabResult(patient_id=6, doctor_id=3, test_name='Free T4',             test_date='2026-01-22', result_value='0.7',     unit='ng/dL', normal_range='0.8-1.8',  is_abnormal=1),
    LabResult(patient_id=8, doctor_id=1, test_name='Haemoglobin',         test_date='2026-02-15', result_value='9.8',     unit='g/dL',  normal_range='12.0-16.0',is_abnormal=1),
    LabResult(patient_id=8, doctor_id=1, test_name='Ferritin',            test_date='2026-02-15', result_value='5',       unit='ng/mL', normal_range='12-150',   is_abnormal=1),
])

session.add_all([
    Vaccination(patient_id=1, vaccine_name='Influenza',           administered_at='2025-10-05', next_due_date='2026-10-05', administered_by='Dr. Olivia Park'),
    Vaccination(patient_id=1, vaccine_name='Tetanus (Td)',        administered_at='2022-03-10', next_due_date='2032-03-10', administered_by='Dr. Olivia Park'),
    Vaccination(patient_id=2, vaccine_name='COVID-19 Booster',   administered_at='2025-09-15', next_due_date='2026-09-15', administered_by='Dr. Olivia Park'),
    Vaccination(patient_id=2, vaccine_name='Influenza',           administered_at='2025-09-15', next_due_date='2026-09-15', administered_by='Dr. Olivia Park'),
    Vaccination(patient_id=3, vaccine_name='Influenza',           administered_at='2024-10-20', next_due_date='2025-10-20', administered_by='Dr. Olivia Park'),
    Vaccination(patient_id=3, vaccine_name='Pneumococcal',        administered_at='2023-01-15', next_due_date=None,         administered_by='Dr. Sara Mendez'),
    Vaccination(patient_id=4, vaccine_name='HPV',                 administered_at='2025-06-01', next_due_date='2025-12-01', administered_by='Dr. Olivia Park'),
    Vaccination(patient_id=5, vaccine_name='Influenza',           administered_at='2025-11-10', next_due_date='2026-11-10', administered_by='Dr. Nathan Brooks'),
    Vaccination(patient_id=5, vaccine_name='Shingles (Shingrix)', administered_at='2024-06-20', next_due_date='2025-06-20', administered_by='Dr. Nathan Brooks'),
    Vaccination(patient_id=6, vaccine_name='COVID-19 Booster',   administered_at='2025-11-22', next_due_date='2026-11-22', administered_by='Dr. Sara Mendez'),
    Vaccination(patient_id=7, vaccine_name='Tetanus (Td)',        administered_at='2021-08-07', next_due_date='2031-08-07', administered_by='Dr. Ahmed Farouk'),
    Vaccination(patient_id=8, vaccine_name='Influenza',           administered_at='2025-10-30', next_due_date='2026-10-30', administered_by='Dr. Olivia Park'),
])
session.commit()


# ── Queries ───────────────────────────────────────────────────────────────────

# ── Query 1: Active prescriptions for a specific patient ──────────────────────
# Joins prescriptions → medical_records → doctors, filtering by patient and
# is_active=1.  Returns only rows for the requested patient's active meds.
print("=" * 70)
print("QUERY 1  Active prescriptions for James Walker (patient_id=1)")
print("=" * 70)

q1 = (
    session.query(
        Prescription.medication_name,
        Prescription.dosage,
        Prescription.frequency,
        Prescription.start_date,
        Prescription.end_date,
        MedicalRecord.diagnosis,
        (Doctor.first_name + ' ' + Doctor.last_name).label('prescribed_by'),
    )
    .join(MedicalRecord, Prescription.record_id == MedicalRecord.record_id)
    .join(Doctor, MedicalRecord.doctor_id == Doctor.doctor_id)
    .filter(MedicalRecord.patient_id == 1, Prescription.is_active == 1)
    .order_by(Prescription.start_date.desc())
    .all()
)
for row in q1:
    print(row)


# ── Query 2: Complete visit history for a specific patient ────────────────────
# Joins medical_records → doctors, returning every visit for the patient
# ordered newest-first.
print("\n" + "=" * 70)
print("QUERY 2  Visit history for Carlos Ramirez (patient_id=3)")
print("=" * 70)

q2 = (
    session.query(
        MedicalRecord.visit_date,
        (Doctor.first_name + ' ' + Doctor.last_name).label('doctor'),
        Doctor.specialization,
        MedicalRecord.diagnosis,
        MedicalRecord.treatment,
        MedicalRecord.notes,
    )
    .join(Doctor, MedicalRecord.doctor_id == Doctor.doctor_id)
    .filter(MedicalRecord.patient_id == 3)
    .order_by(MedicalRecord.visit_date.desc())
    .all()
)
for row in q2:
    print(row)


# ── Query 3: Patients with at least one abnormal lab result ───────────────────
# Aggregates lab_results grouped by patient; the WHERE clause restricts to
# is_abnormal=1 rows only, so no Python-side filtering is needed.
print("\n" + "=" * 70)
print("QUERY 3  Patients with abnormal lab results")
print("=" * 70)

q3 = (
    session.query(
        (Patient.first_name + ' ' + Patient.last_name).label('patient'),
        Patient.date_of_birth,
        func.count(LabResult.result_id).label('abnormal_results'),
        func.max(LabResult.test_date).label('most_recent_abnormal'),
        func.group_concat(distinct(LabResult.test_name)).label('tests_flagged'),
    )
    .join(Patient, LabResult.patient_id == Patient.patient_id)
    .filter(LabResult.is_abnormal == 1)
    .group_by(LabResult.patient_id)
    .order_by(func.count(LabResult.result_id).desc())
    .all()
)
for row in q3:
    print(row)


# ── Query 4: Scheduled appointments for a specific doctor ─────────────────────
# Joins appointments → patients, filtering by doctor_id and status='scheduled'
# so only upcoming/pending appointments are returned.
print("\n" + "=" * 70)
print("QUERY 4  Scheduled appointments for Dr. Nathan Brooks (doctor_id=2)")
print("=" * 70)

q4 = (
    session.query(
        Appointment.scheduled_at,
        Appointment.duration_minutes,
        (Patient.first_name + ' ' + Patient.last_name).label('patient'),
        Patient.phone.label('patient_phone'),
        Appointment.reason,
        Appointment.status,
    )
    .join(Patient, Appointment.patient_id == Patient.patient_id)
    .filter(Appointment.doctor_id == 2, Appointment.status == 'scheduled')
    .order_by(Appointment.scheduled_at)
    .all()
)
for row in q4:
    print(row)

session.close()
