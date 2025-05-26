from datetime import date, datetime # Added datetime for parsing
from models import Patient, Staff, Surgeon, OperatingRoom, SurgeryEquipment, Surgery # Added Surgery model


def initialize_patients():
    return [
        {
            "patient_id": "P001",
            "name": "John Doe",
            "dob": "1990-01-01",
            "contact_info": {"phone": "555-0100", "email": "john.doe@example.com"},
            "medical_history": [
                {"condition": "Condition A", "date_diagnosed": "2018-05-01"},
                {"condition": "Condition B", "date_diagnosed": "2019-11-15"},
                # Add more medical history records as needed
            ],
            "privacy_consent": True,
        },
        # Add more patient documents as needed...
    ]


def initialize_patients_sqlalchemy():
    return [
        Patient( # ID will be auto-generated (1)
            name="John Doe",
            dob=date(1990, 1, 1),
            contact_info="555-0100, john.doe@example.com",
            privacy_consent=True,
        ),
        Patient( # ID will be auto-generated (2)
            name="Jane Smith",
            dob=date(1985, 5, 10),
            contact_info="555-0102, jane.smith@example.com",
            privacy_consent=True,
        ),
        Patient( # ID will be auto-generated (3)
            name="Alice Brown",
            dob=date(1970, 8, 20),
            contact_info="555-0103, alice.brown@example.com",
            privacy_consent=False,
        ),
    ]


def initialize_staff_members():
    return [
        {
            "staff_id": "S001",
            "name": "Jane Smith",
            "role": "Nurse",
            "specialization": None,  # This can be null/None for non-surgeons
            "contact_info": {"phone": "555-0101", "email": "jane.smith@example.com"},
            "availability_schedule": [
                {"day": "Monday", "start": "08:00", "end": "17:00"},
                {"day": "Tuesday", "start": "08:00", "end": "17:00"},
                # Add more availability slots as needed
            ],
        },
        # Add more staff member documents as needed...
    ]


def initialize_staff_members_sqlalchemy():
    return [
        Staff(
            name="Jane Smith",
            role="Nurse",
            specialization=None,
            contact_info="555-0101, jane.smith@example.com",
            availability=True,
        ),
        # Add more Staff instances as needed
    ]


def initialize_surgeons():
    return [
        {
            "surgeon_id": "S001",
            "name": "Dr. Emily Smith",
            "contact_info": {"email": "emily.smith@example.com", "phone": "555-0101"},
            "specialization": "Cardiothoracic Surgery",
            "credentials": [
                "Board Certified in Thoracic Surgery",
                "MD from Example Medical School",
            ],
            "availability": [
                {"day": "Monday", "start": "08:00", "end": "16:00"},
                {"day": "Wednesday", "start": "08:00", "end": "16:00"},
            ],
            "surgeon_preferences": {"preferred_operating_room": "OR1"},
        },
        {
            "surgeon_id": "S002",
            "name": "Dr. John Doe",
            "contact_info": {"email": "john.doe@example.com", "phone": "555-0202"},
            "specialization": "Orthopedic Surgery",
            "credentials": [
                "Board Certified in Orthopedic Surgery",
                "MD from Another Example Medical School",
            ],
            "availability": [
                {"day": "Tuesday", "start": "10:00", "end": "18:00"},
                {"day": "Thursday", "start": "10:00", "end": "18:00"},
            ],
            "surgeon_preferences": {"preferred_operating_room": "OR2"},
        },
        # Add more surgeons as needed
    ]


def initialize_surgeons_sqlalchemy():
    return [
        Surgeon( # ID will be auto-generated (1)
            name="Dr. Emily Smith",
            contact_info="555-0101, emily.smith@example.com",
            specialization="Cardiothoracic Surgery",
            credentials="Board Certified in Thoracic Surgery; MD from Example Medical School",
            availability=True,
        ),
        Surgeon( # ID will be auto-generated (2)
            name="Dr. John Doe",
            contact_info="555-0202, john.doe@example.com",
            specialization="Orthopedic Surgery",
            credentials="Board Certified in Orthopedic Surgery; MD from Another Example Medical School",
            availability=True,
        ),
        Surgeon( # ID will be auto-generated (3)
            name="Dr. Alan Turing",
            contact_info="555-0303, alan.turing@example.com",
            specialization="Neurosurgery",
            credentials="MD, PhD, FRCSEd",
            availability=True,
        ),
    ]


def initialize_operating_rooms():
    return [
        {
            "room_id": "OR001",
            "location": "Main Building - Room 101",
            "equipment_list": [],
        },
        # Add more operating room documents as needed...
    ]


def initialize_operating_rooms_sqlalchemy():
    return [
        OperatingRoom(location="Main Building - Room 101"), # ID will be auto-generated (1)
        OperatingRoom(location="Main Building - Room 102"), # ID will be auto-generated (2)
        OperatingRoom(location="West Wing - Room 201"),    # ID will be auto-generated (3)
        OperatingRoom(location="East Wing - Room A"),      # ID will be auto-generated (4)
    ]


def initialize_surgeries():
    return [
        {
            "surgery_id": "SUR001",
            "patient_id": "P001",
            "scheduled_date": "2023-07-01",  # Use an actual date
            "estimated_start_time": "08:00",  # New
            "estimated_end_time": "10:00",  # New
            "surgery_type": "Appendectomy",
            "urgency_level": "High",
            "duration": 120,
            "status": "Scheduled",
            "priority": "Normal",
        },
        # Add more surgery documents as needed...
    ]

def initialize_surgeries_sqlalchemy():
    # First, we need to create surgery types
    from db_config import SessionLocal

    # Create a session to check if surgery types exist
    db = SessionLocal()
    try:
        # Check if we have surgery types
        from models import SurgeryType
        surgery_types = db.query(SurgeryType).all()

        # If no surgery types exist, create them
        if not surgery_types:
            surgery_types = [
                SurgeryType(name="Appendectomy", description="Removal of the appendix"),
                SurgeryType(name="Knee Replacement", description="Total knee arthroplasty"),
                SurgeryType(name="Craniotomy", description="Surgical opening of the skull"),
                SurgeryType(name="Coronary Bypass", description="Coronary artery bypass grafting"),
                SurgeryType(name="Hip Arthroscopy", description="Minimally invasive hip surgery")
            ]
            db.add_all(surgery_types)
            db.commit()

            # Refresh to get the IDs
            for st in surgery_types:
                db.refresh(st)

        # Create a mapping of surgery type names to IDs
        surgery_type_map = {st.name: st.type_id for st in surgery_types}

    finally:
        db.close()

    # Define surgeries with surgery_type_id instead of surgery_type
    return [
        Surgery( # surgery_id will be auto-generated
            patient_id=1,
            surgeon_id=1,
            surgery_type_id=surgery_type_map.get("Appendectomy", 1),
            scheduled_date=datetime(2024, 7, 1, 8, 0, 0),
            start_time=datetime(2024, 7, 1, 8, 0, 0),
            end_time=datetime(2024, 7, 1, 10, 0, 0),
            duration_minutes=120,
            status="Scheduled",
            urgency_level="High"
        ),
        Surgery(
            patient_id=2,
            surgeon_id=2,
            surgery_type_id=surgery_type_map.get("Knee Replacement", 2),
            scheduled_date=datetime(2024, 7, 1, 10, 30, 0),
            start_time=datetime(2024, 7, 1, 10, 30, 0),
            end_time=datetime(2024, 7, 1, 13, 0, 0),
            duration_minutes=150,
            status="Scheduled",
            urgency_level="Medium"
        ),
        Surgery(
            patient_id=3,
            surgeon_id=3,
            surgery_type_id=surgery_type_map.get("Craniotomy", 3),
            scheduled_date=datetime(2024, 7, 2, 9, 0, 0),
            start_time=datetime(2024, 7, 2, 9, 0, 0),
            end_time=datetime(2024, 7, 2, 14, 0, 0),
            duration_minutes=300,
            status="Scheduled",
            urgency_level="High"
        ),
        Surgery(
            patient_id=1,
            surgeon_id=1,
            surgery_type_id=surgery_type_map.get("Coronary Bypass", 4),
            scheduled_date=datetime(2024, 7, 3, 8, 0, 0),
            start_time=datetime(2024, 7, 3, 8, 0, 0),
            end_time=datetime(2024, 7, 3, 12, 0, 0),
            duration_minutes=240,
            status="Scheduled",
            urgency_level="High"
        ),
        Surgery(
            patient_id=2,
            surgeon_id=2,
            surgery_type_id=surgery_type_map.get("Hip Arthroscopy", 5),
            scheduled_date=datetime(2024, 7, 4, 13, 0, 0),
            start_time=datetime(2024, 7, 4, 13, 0, 0),
            end_time=datetime(2024, 7, 4, 15, 0, 0),
            duration_minutes=120,
            status="Scheduled",
            urgency_level="Low"
        ),
    ]




def initialize_surgery_equipments():
    return [
        {
            "equipment_id": "EQ001",
            "name": "Scalpel",
            "type": "Tool",
            "availability": True,
        },
        # Add more surgery equipment documents as needed...
    ]


def initialize_surgery_equipments_sqlalchemy():
    return [
        SurgeryEquipment(name="Scalpel", type="Tool", availability=True),
        # Add more SurgeryEquipment instances as needed
    ]


def initialize_surgery_equipment_usages():
    return [
        {"usage_id": "EU001", "surgery_id": "SUR001", "equipment_id": "EQ001"},
        # Add more surgery equipment usage documents as needed...
    ]


def initialize_surgery_room_assignments():
    return [
        {
            "assignment_id": "RA001",
            "surgery_id": "SUR001",
            "room_id": "OR001",
            "start_time": "2023-07-01 08:00",
            "end_time": "2023-07-01 10:00",
        },
        # Add more surgery room assignment documents as needed...
    ]


def initialize_surgery_staff_assignments():
    return [
        {
            "assignment_id": "SA001",
            "surgery_id": "SUR001",
            "staff_id": "S002",
            "role": "Surgeon",
        },
        # Add more surgery staff assignment documents as needed...
    ]


def initialize_surgery_appointments():
    return [
        {
            "appointment_id": "APPT001",
            "surgery_id": "SUR001",
            "patient_id": "P001",
            "staff_assignments": [
                {"staff_id": "S002", "role": "Lead Surgeon"}
                # Add more staff assignments as needed
            ],
            "room_id": "OR001",
            "start_time": "2023-07-01T09:00:00",
            "end_time": "2023-07-01T11:00:00",
        },
        # Add more appointments as needed...
    ]
