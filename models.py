from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Enum as GenericEnum,  # Changed from MySQLEnum
)
from sqlalchemy.orm import relationship
from db_config import Base


class OperatingRoom(Base):
    __tablename__ = "operatingroom"
    room_id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(255), nullable=False)
    surgeries = relationship("Surgery", back_populates="room")
    equipment = relationship("OperatingRoomEquipment", back_populates="room")


class Patient(Base):
    __tablename__ = "patient"
    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    contact_info = Column(String(255), nullable=True)
    privacy_consent = Column(Boolean, nullable=False, server_default="0")
    surgeries = relationship("Surgery", back_populates="patient")
    appointments = relationship("SurgeryAppointment", back_populates="patient")
    medical_history = relationship("PatientMedicalHistory", back_populates="patient")


class Staff(Base):
    __tablename__ = "staff"
    staff_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    contact_info = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)
    availability = Column(Boolean, nullable=False, server_default="1")
    assignments = relationship("SurgeryStaffAssignment", back_populates="staff")


class Surgeon(Base):
    __tablename__ = "surgeon"
    surgeon_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    contact_info = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=False)
    credentials = Column(Text, nullable=False)
    availability = Column(Boolean, nullable=False, server_default="1")
    surgeries = relationship("Surgery", back_populates="surgeon")
    appointments = relationship("SurgeryAppointment", back_populates="surgeon")
    preferences = relationship("SurgeonPreference", back_populates="surgeon")


class SurgeryEquipment(Base):
    __tablename__ = "surgeryequipment"
    equipment_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    availability = Column(Boolean, nullable=False, server_default="1")
    usages = relationship("SurgeryEquipmentUsage", back_populates="equipment")


class Surgery(Base):
    __tablename__ = "surgery"
    surgery_id = Column(Integer, primary_key=True, autoincrement=True)
    scheduled_date = Column(DateTime, nullable=False)
    # surgery_type = Column(String(100), nullable=False) # Original line being replaced
    surgery_type_id = Column(Integer, ForeignKey("surgerytype.type_id", ondelete="RESTRICT"), nullable=False)
    surgery_type_details = relationship("SurgeryType", back_populates="surgeries")
    # Changed MySQLEnum to GenericEnum with native_enum=False
    urgency_level = Column(
        GenericEnum(
            "Low", "Medium", "High", name="urgency_level_enum", native_enum=False
        ),
        nullable=False,
    )
    duration_minutes = Column(Integer, nullable=False)
    # Changed MySQLEnum to GenericEnum with native_enum=False
    status = Column(
        GenericEnum(
            "Scheduled",
            "In Progress",
            "Completed",
            "Cancelled",
            name="surgery_status_enum",
            native_enum=False,
        ),
        nullable=False,
        server_default="Scheduled",
    )
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    patient_id = Column(
        Integer,
        ForeignKey("patient.patient_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
    )
    surgeon_id = Column(
        Integer,
        ForeignKey("surgeon.surgeon_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
    )
    room_id = Column(
        Integer,
        ForeignKey("operatingroom.room_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
    )
    patient = relationship("Patient", back_populates="surgeries")
    surgeon = relationship("Surgeon", back_populates="surgeries")
    room = relationship("OperatingRoom", back_populates="surgeries")
    equipment_usages = relationship("SurgeryEquipmentUsage", back_populates="surgery")
    staff_assignments = relationship("SurgeryStaffAssignment", back_populates="surgery")


class OperatingRoomEquipment(Base):
    __tablename__ = "operatingroomequipment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(
        Integer,
        ForeignKey("operatingroom.room_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    equipment_name = Column(String(255), nullable=False)
    room = relationship("OperatingRoom", back_populates="equipment")


class PatientMedicalHistory(Base):
    __tablename__ = "patientmedicalhistory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(
        Integer,
        ForeignKey("patient.patient_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    medical_condition = Column(String(255), nullable=False)
    diagnosis_date = Column(Date, nullable=False)
    patient = relationship("Patient", back_populates="medical_history")


class SurgeryEquipmentUsage(Base):
    __tablename__ = "surgeryequipmentusage"
    usage_id = Column(Integer, primary_key=True, autoincrement=True)
    surgery_id = Column(
        Integer,
        ForeignKey("surgery.surgery_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    equipment_id = Column(
        Integer,
        ForeignKey(
            "surgeryequipment.equipment_id", ondelete="RESTRICT", onupdate="CASCADE"
        ),
    )
    usage_start_time = Column(DateTime, nullable=True)  # Added this line
    usage_end_time = Column(DateTime, nullable=True)  # Added this line
    surgery = relationship("Surgery", back_populates="equipment_usages")
    equipment = relationship("SurgeryEquipment", back_populates="usages")


class SurgeryStaffAssignment(Base):
    __tablename__ = "surgerystaffassignment"
    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    surgery_id = Column(
        Integer,
        ForeignKey("surgery.surgery_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    staff_id = Column(
        Integer, ForeignKey("staff.staff_id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    role = Column(String(100), nullable=False)
    surgery = relationship("Surgery", back_populates="staff_assignments")
    staff = relationship("Staff", back_populates="assignments")


class SurgeryAppointment(Base):
    __tablename__ = "surgeryappointment"
    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(
        Integer,
        ForeignKey("patient.patient_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    surgeon_id = Column(
        Integer,
        ForeignKey("surgeon.surgeon_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    room_id = Column(
        Integer,
        ForeignKey("operatingroom.room_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    appointment_date = Column(DateTime, nullable=False)
    # Changed MySQLEnum to GenericEnum with native_enum=False
    status = Column(
        GenericEnum(
            "Scheduled",
            "Completed",
            "Cancelled",
            name="appointment_status_enum",
            native_enum=False,
        ),
        nullable=False,
        server_default="Scheduled",
    )
    notes = Column(Text, nullable=True)
    patient = relationship("Patient", back_populates="appointments")
    surgeon = relationship("Surgeon", back_populates="appointments")
    room = relationship("OperatingRoom")


class SurgeonPreference(Base):
    __tablename__ = "surgeonpreference"
    preference_id = Column(Integer, primary_key=True, autoincrement=True)
    surgeon_id = Column(
        Integer,
        ForeignKey("surgeon.surgeon_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    preference_type = Column(String(100), nullable=False)
    preference_value = Column(String(255), nullable=False)
    surgeon = relationship("Surgeon", back_populates="preferences")


class SurgeonAvailability(Base):
    __tablename__ = "surgeonavailability"
    availability_id = Column(Integer, primary_key=True, autoincrement=True)
    surgeon_id = Column(
        Integer,
        ForeignKey("surgeon.surgeon_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    day_of_week = Column(String(10), nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(String(5), nullable=False)  # Format: "HH:MM"
    end_time = Column(String(5), nullable=False)  # Format: "HH:MM"


class SurgeryRoomAssignment(Base):
    __tablename__ = "surgeryroomassignment"
    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    surgery_id = Column(
        Integer,
        ForeignKey("surgery.surgery_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    room_id = Column(
        Integer,
        ForeignKey("operatingroom.room_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


class SurgeryType(Base):
    __tablename__ = "surgerytype"
    type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Relationship to Surgery, indicating which surgeries are of this type
    surgeries = relationship("Surgery", back_populates="surgery_type_details")

    # Relationships to SequenceDependentSetupTime
    # Setup times where this surgery type is the preceding type
    setups_from_this_type = relationship(
        "SequenceDependentSetupTime",
        foreign_keys="[SequenceDependentSetupTime.from_surgery_type_id]",
        back_populates="from_surgery_type_details"
    )
    # Setup times where this surgery type is the succeeding type
    setups_to_this_type = relationship(
        "SequenceDependentSetupTime",
        foreign_keys="[SequenceDependentSetupTime.to_surgery_type_id]",
        back_populates="to_surgery_type_details"
    )

    def __repr__(self):
        return f"<SurgeryType(type_id={self.type_id}, name='{self.name}')>"


class SequenceDependentSetupTime(Base):
    __tablename__ = "sequencedependentsetuptime"
    id = Column(Integer, primary_key=True, autoincrement=True)

    from_surgery_type_id = Column(
        Integer,
        ForeignKey("surgerytype.type_id", ondelete="CASCADE"),
        nullable=False
    )
    to_surgery_type_id = Column(
        Integer,
        ForeignKey("surgerytype.type_id", ondelete="CASCADE"),
        nullable=False
    )
    setup_time_minutes = Column(Integer, nullable=False)

    # Relationships to SurgeryType
    from_surgery_type_details = relationship(
        "SurgeryType",
        foreign_keys=[from_surgery_type_id],
        back_populates="setups_from_this_type"
    )
    to_surgery_type_details = relationship(
        "SurgeryType",
        foreign_keys=[to_surgery_type_id],
        back_populates="setups_to_this_type"
    )


class User(Base):
    """
    User model for authentication and authorization.

    This model stores user information for authentication and authorization.
    """
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, server_default="user")
    staff_id = Column(Integer, ForeignKey("staff.staff_id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="1")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_login = Column(DateTime, nullable=True)

    # Relationship to Staff
    staff = relationship("Staff")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', role='{self.role}')>"


class AuditLog(Base):
    """
    Audit log for tracking changes to entities and user actions.

    This model stores audit events for compliance and security purposes.
    """
    __tablename__ = "auditlog"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    user_id = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)

    def __repr__(self):
        return f"<AuditLog(log_id={self.log_id}, timestamp={self.timestamp}, action='{self.action}', entity_type='{self.entity_type}', entity_id={self.entity_id})>"
