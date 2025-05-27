"""
Advanced Feasibility Checker for Task 2.3.

This module provides enhanced constraint validation including:
- Equipment availability checking with advanced constraints
- Staff availability constraints
- Surgeon specialization matching
- Custom constraint configuration
- Constraint violation reporting
"""

import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from models import (
    Surgery, OperatingRoom, Surgeon, SurgeryEquipment, SurgeryRoomAssignment,
    SurgeryEquipmentUsage, SurgeryType, SurgeonPreference, SurgeonAvailability,
    OperatingRoomEquipment, Staff, SurgeryStaffAssignment
)
from api.models import (
    ConstraintType, ConstraintSeverity, ConstraintViolation, ConstraintConfiguration,
    FeasibilityCheckRequest, FeasibilityCheckResult, StaffAvailabilityConstraint,
    SurgeonSpecializationConstraint, EquipmentAvailabilityConstraint, CustomConstraintRule
)
from feasibility_checker import FeasibilityChecker

logger = logging.getLogger(__name__)


class AdvancedFeasibilityChecker(FeasibilityChecker):
    """
    Advanced feasibility checker with enhanced constraint validation.

    Extends the base FeasibilityChecker with:
    - Advanced equipment availability checking
    - Staff availability constraints
    - Surgeon specialization matching
    - Custom constraint configuration
    - Detailed violation reporting
    """

    def __init__(self, db_session: Session):
        """
        Initialize the advanced feasibility checker.

        Args:
            db_session: Database session
        """
        super().__init__(db_session)

        # Advanced constraint configurations
        self.constraint_configurations: Dict[str, ConstraintConfiguration] = {}
        self.custom_rules: Dict[str, CustomConstraintRule] = {}

        # Constraint caches
        self.staff_availability_cache: Dict[int, List[StaffAvailabilityConstraint]] = {}
        self.surgeon_specialization_cache: Dict[int, SurgeonSpecializationConstraint] = {}
        self.equipment_constraints_cache: Dict[int, EquipmentAvailabilityConstraint] = {}

        # Load default constraints
        self._load_default_constraints()

        logger.info("Advanced feasibility checker initialized")

    def _load_default_constraints(self):
        """Load default constraint configurations."""

        # Equipment availability constraint
        self.constraint_configurations["equipment_availability"] = ConstraintConfiguration(
            constraint_id="equipment_availability",
            constraint_type=ConstraintType.EQUIPMENT_AVAILABILITY,
            name="Equipment Availability",
            description="Ensures required equipment is available during surgery time",
            severity=ConstraintSeverity.CRITICAL,
            parameters={
                "check_maintenance_windows": True,
                "check_concurrent_usage": True,
                "include_setup_cleanup_time": True
            }
        )

        # Staff availability constraint
        self.constraint_configurations["staff_availability"] = ConstraintConfiguration(
            constraint_id="staff_availability",
            constraint_type=ConstraintType.STAFF_AVAILABILITY,
            name="Staff Availability",
            description="Ensures required staff are available during surgery time",
            severity=ConstraintSeverity.CRITICAL,
            parameters={
                "check_working_hours": True,
                "check_concurrent_assignments": True,
                "check_daily_hour_limits": True,
                "check_qualifications": True
            }
        )

        # Surgeon specialization constraint
        self.constraint_configurations["surgeon_specialization"] = ConstraintConfiguration(
            constraint_id="surgeon_specialization",
            constraint_type=ConstraintType.SURGEON_SPECIALIZATION,
            name="Surgeon Specialization",
            description="Ensures surgeon is qualified for the surgery type",
            severity=ConstraintSeverity.CRITICAL,
            parameters={
                "check_qualifications": True,
                "check_experience_level": True,
                "check_restrictions": True,
                "allow_supervision": True
            }
        )

        # Room capacity constraint
        self.constraint_configurations["room_capacity"] = ConstraintConfiguration(
            constraint_id="room_capacity",
            constraint_type=ConstraintType.ROOM_CAPACITY,
            name="Room Capacity",
            description="Ensures room has sufficient capacity for surgery requirements",
            severity=ConstraintSeverity.HIGH,
            parameters={
                "check_physical_space": True,
                "check_equipment_space": True,
                "check_staff_capacity": True
            }
        )

    def check_feasibility_advanced(self, request: FeasibilityCheckRequest) -> FeasibilityCheckResult:
        """
        Perform advanced feasibility check with detailed violation reporting.

        Args:
            request: Feasibility check request

        Returns:
            FeasibilityCheckResult: Detailed feasibility check result
        """
        start_time = time.time()
        violations = []
        warnings = []
        constraints_checked = 0

        # Get surgery details
        surgery = self.db_session.query(Surgery).filter(
            Surgery.surgery_id == request.surgery_id
        ).first()

        if not surgery:
            violation = ConstraintViolation(
                constraint_id="surgery_existence",
                constraint_type=ConstraintType.RESOURCE_CONFLICT,
                severity=ConstraintSeverity.CRITICAL,
                description=f"Surgery {request.surgery_id} not found",
                surgery_id=request.surgery_id,
                suggested_actions=["Verify surgery ID", "Check if surgery exists in database"]
            )
            violations.append(violation)

            return FeasibilityCheckResult(
                is_feasible=False,
                surgery_id=request.surgery_id,
                room_id=request.room_id,
                start_time=request.start_time,
                end_time=request.end_time,
                violations=violations,
                warnings=warnings,
                check_duration_ms=(time.time() - start_time) * 1000,
                constraints_checked=1,
                equipment_feasible=False,
                staff_feasible=False,
                specialization_feasible=False,
                room_feasible=False
            )

        # Check basic feasibility first
        basic_feasible = self.is_feasible(
            request.surgery_id,
            request.room_id,
            request.start_time,
            request.end_time,
            request.current_assignments or [],
            request.ignore_surgery_id
        )

        # Room availability check
        room_feasible = True
        if not self.is_room_available(
            request.room_id, request.start_time, request.end_time,
            request.current_assignments or [], request.ignore_surgery_id
        ):
            room_feasible = False
            violation = ConstraintViolation(
                constraint_id="room_availability",
                constraint_type=ConstraintType.RESOURCE_CONFLICT,
                severity=ConstraintSeverity.CRITICAL,
                description=f"Room {request.room_id} is not available during requested time",
                surgery_id=request.surgery_id,
                room_id=request.room_id,
                start_time=request.start_time,
                end_time=request.end_time,
                suggested_actions=[
                    "Choose a different time slot",
                    "Select an alternative room",
                    "Check for scheduling conflicts"
                ]
            )
            violations.append(violation)
        constraints_checked += 1

        # Equipment availability check
        equipment_feasible = True
        if request.check_equipment:
            equipment_violations = self._check_equipment_availability_advanced(
                surgery, request.room_id, request.start_time, request.end_time
            )
            violations.extend(equipment_violations)
            equipment_feasible = len(equipment_violations) == 0
            constraints_checked += 1

        # Staff availability check
        staff_feasible = True
        if request.check_staff:
            staff_violations = self._check_staff_availability_advanced(
                surgery, request.room_id, request.start_time, request.end_time
            )
            violations.extend(staff_violations)
            staff_feasible = len(staff_violations) == 0
            constraints_checked += 1

        # Surgeon specialization check
        specialization_feasible = True
        if request.check_specialization and surgery.surgeon_id:
            specialization_violations = self._check_surgeon_specialization_advanced(
                surgery.surgeon_id, surgery.surgery_type_id
            )
            violations.extend(specialization_violations)
            specialization_feasible = len(specialization_violations) == 0
            constraints_checked += 1

        # Custom constraints check
        if request.check_custom_constraints:
            custom_violations = self._check_custom_constraints(
                surgery, request.room_id, request.start_time, request.end_time
            )
            violations.extend(custom_violations)
            constraints_checked += len(self.custom_rules)

        # Generate recommendations
        recommendations = self._generate_recommendations(violations, surgery)

        # Calculate overall feasibility
        is_feasible = (
            room_feasible and equipment_feasible and
            staff_feasible and specialization_feasible and
            len([v for v in violations if v.severity == ConstraintSeverity.CRITICAL]) == 0
        )

        return FeasibilityCheckResult(
            is_feasible=is_feasible,
            surgery_id=request.surgery_id,
            room_id=request.room_id,
            start_time=request.start_time,
            end_time=request.end_time,
            violations=violations,
            warnings=warnings,
            check_duration_ms=(time.time() - start_time) * 1000,
            constraints_checked=constraints_checked,
            equipment_feasible=equipment_feasible,
            staff_feasible=staff_feasible,
            specialization_feasible=specialization_feasible,
            room_feasible=room_feasible,
            recommendations=recommendations
        )

    def _check_equipment_availability_advanced(
        self,
        surgery: Surgery,
        room_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[ConstraintViolation]:
        """Check advanced equipment availability constraints."""
        violations = []

        # Get equipment requirements for this surgery
        equipment_usages = self.db_session.query(SurgeryEquipmentUsage).filter(
            SurgeryEquipmentUsage.surgery_id == surgery.surgery_id
        ).all()

        for usage in equipment_usages:
            equipment = self.db_session.query(SurgeryEquipment).filter(
                SurgeryEquipment.equipment_id == usage.equipment_id
            ).first()

            if not equipment:
                violation = ConstraintViolation(
                    constraint_id=f"equipment_existence_{usage.equipment_id}",
                    constraint_type=ConstraintType.EQUIPMENT_AVAILABILITY,
                    severity=ConstraintSeverity.CRITICAL,
                    description=f"Required equipment {usage.equipment_id} not found",
                    surgery_id=surgery.surgery_id,
                    equipment_id=usage.equipment_id,
                    suggested_actions=["Verify equipment ID", "Check equipment inventory"]
                )
                violations.append(violation)
                continue

            # Check basic availability
            if not equipment.availability:
                violation = ConstraintViolation(
                    constraint_id=f"equipment_unavailable_{equipment.equipment_id}",
                    constraint_type=ConstraintType.EQUIPMENT_AVAILABILITY,
                    severity=ConstraintSeverity.CRITICAL,
                    description=f"Equipment '{equipment.name}' is marked as unavailable",
                    surgery_id=surgery.surgery_id,
                    equipment_id=equipment.equipment_id,
                    suggested_actions=[
                        "Check equipment maintenance status",
                        "Find alternative equipment",
                        "Reschedule surgery"
                    ]
                )
                violations.append(violation)
                continue

            # Check for concurrent usage conflicts
            conflicting_usages = self.db_session.query(SurgeryEquipmentUsage).filter(
                SurgeryEquipmentUsage.equipment_id == equipment.equipment_id,
                SurgeryEquipmentUsage.surgery_id != surgery.surgery_id,
                SurgeryEquipmentUsage.usage_start_time < end_time,
                SurgeryEquipmentUsage.usage_end_time > start_time
            ).all()

            if conflicting_usages:
                for conflict in conflicting_usages:
                    violation = ConstraintViolation(
                        constraint_id=f"equipment_conflict_{equipment.equipment_id}_{conflict.surgery_id}",
                        constraint_type=ConstraintType.EQUIPMENT_AVAILABILITY,
                        severity=ConstraintSeverity.CRITICAL,
                        description=f"Equipment '{equipment.name}' is already in use by surgery {conflict.surgery_id}",
                        surgery_id=surgery.surgery_id,
                        equipment_id=equipment.equipment_id,
                        start_time=start_time,
                        end_time=end_time,
                        suggested_actions=[
                            "Choose a different time slot",
                            "Find alternative equipment",
                            "Coordinate with other surgery"
                        ]
                    )
                    violations.append(violation)

        return violations

    def _check_staff_availability_advanced(
        self,
        surgery: Surgery,
        room_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[ConstraintViolation]:
        """Check advanced staff availability constraints."""
        violations = []

        # Get staff assignments for this surgery
        staff_assignments = self.db_session.query(SurgeryStaffAssignment).filter(
            SurgeryStaffAssignment.surgery_id == surgery.surgery_id
        ).all()

        for assignment in staff_assignments:
            staff = self.db_session.query(Staff).filter(
                Staff.staff_id == assignment.staff_id
            ).first()

            if not staff:
                violation = ConstraintViolation(
                    constraint_id=f"staff_existence_{assignment.staff_id}",
                    constraint_type=ConstraintType.STAFF_AVAILABILITY,
                    severity=ConstraintSeverity.CRITICAL,
                    description=f"Required staff member {assignment.staff_id} not found",
                    surgery_id=surgery.surgery_id,
                    staff_id=assignment.staff_id,
                    suggested_actions=["Verify staff ID", "Assign alternative staff member"]
                )
                violations.append(violation)
                continue

            # Check basic availability
            if not staff.availability:
                violation = ConstraintViolation(
                    constraint_id=f"staff_unavailable_{staff.staff_id}",
                    constraint_type=ConstraintType.STAFF_AVAILABILITY,
                    severity=ConstraintSeverity.CRITICAL,
                    description=f"Staff member '{staff.name}' is marked as unavailable",
                    surgery_id=surgery.surgery_id,
                    staff_id=staff.staff_id,
                    suggested_actions=[
                        "Check staff schedule",
                        "Assign alternative staff member",
                        "Reschedule surgery"
                    ]
                )
                violations.append(violation)
                continue

            # Check for concurrent assignment conflicts
            conflicting_assignments = self.db_session.query(SurgeryStaffAssignment).join(
                SurgeryRoomAssignment, SurgeryStaffAssignment.surgery_id == SurgeryRoomAssignment.surgery_id
            ).filter(
                SurgeryStaffAssignment.staff_id == staff.staff_id,
                SurgeryStaffAssignment.surgery_id != surgery.surgery_id,
                SurgeryRoomAssignment.start_time < end_time,
                SurgeryRoomAssignment.end_time > start_time
            ).all()

            if conflicting_assignments:
                for conflict in conflicting_assignments:
                    violation = ConstraintViolation(
                        constraint_id=f"staff_conflict_{staff.staff_id}_{conflict.surgery_id}",
                        constraint_type=ConstraintType.STAFF_AVAILABILITY,
                        severity=ConstraintSeverity.CRITICAL,
                        description=f"Staff member '{staff.name}' is already assigned to surgery {conflict.surgery_id}",
                        surgery_id=surgery.surgery_id,
                        staff_id=staff.staff_id,
                        start_time=start_time,
                        end_time=end_time,
                        suggested_actions=[
                            "Choose a different time slot",
                            "Assign alternative staff member",
                            "Coordinate with other surgery"
                        ]
                    )
                    violations.append(violation)

        return violations

    def _check_surgeon_specialization_advanced(
        self,
        surgeon_id: int,
        surgery_type_id: int
    ) -> List[ConstraintViolation]:
        """Check advanced surgeon specialization constraints."""
        violations = []

        # Get surgeon details
        surgeon = self.db_session.query(Surgeon).filter(
            Surgeon.surgeon_id == surgeon_id
        ).first()

        if not surgeon:
            violation = ConstraintViolation(
                constraint_id=f"surgeon_existence_{surgeon_id}",
                constraint_type=ConstraintType.SURGEON_SPECIALIZATION,
                severity=ConstraintSeverity.CRITICAL,
                description=f"Surgeon {surgeon_id} not found",
                surgeon_id=surgeon_id,
                suggested_actions=["Verify surgeon ID", "Assign alternative surgeon"]
            )
            violations.append(violation)
            return violations

        # Get surgery type details
        surgery_type = self.db_session.query(SurgeryType).filter(
            SurgeryType.type_id == surgery_type_id
        ).first()

        if not surgery_type:
            violation = ConstraintViolation(
                constraint_id=f"surgery_type_existence_{surgery_type_id}",
                constraint_type=ConstraintType.SURGEON_SPECIALIZATION,
                severity=ConstraintSeverity.CRITICAL,
                description=f"Surgery type {surgery_type_id} not found",
                surgeon_id=surgeon_id,
                suggested_actions=["Verify surgery type ID"]
            )
            violations.append(violation)
            return violations

        # Check if surgeon's specialization matches surgery type requirements
        surgeon_specialization = surgeon.specialization.lower() if surgeon.specialization else ""
        surgery_type_name = surgery_type.name.lower() if surgery_type.name else ""

        # Simple specialization matching (can be enhanced with more sophisticated logic)
        specialization_matches = [
            ("general surgery", ["appendectomy", "gallbladder", "hernia"]),
            ("orthopedic", ["hip", "knee", "shoulder", "spine"]),
            ("cardiac", ["heart", "cardiac", "bypass"]),
            ("neurosurgery", ["brain", "spine", "neurological"]),
            ("plastic surgery", ["reconstruction", "cosmetic"]),
            ("emergency", ["trauma", "emergency"])
        ]

        is_qualified = False
        for specialization, surgery_keywords in specialization_matches:
            if specialization in surgeon_specialization:
                for keyword in surgery_keywords:
                    if keyword in surgery_type_name:
                        is_qualified = True
                        break
                if is_qualified:
                    break

        # If no specific match found, check if it's a general surgery
        if not is_qualified and "general" in surgeon_specialization:
            is_qualified = True  # General surgeons can perform most surgeries

        if not is_qualified:
            violation = ConstraintViolation(
                constraint_id=f"surgeon_specialization_mismatch_{surgeon_id}_{surgery_type_id}",
                constraint_type=ConstraintType.SURGEON_SPECIALIZATION,
                severity=ConstraintSeverity.HIGH,
                description=f"Surgeon '{surgeon.name}' with specialization '{surgeon.specialization}' may not be qualified for surgery type '{surgery_type.name}'",
                surgeon_id=surgeon_id,
                suggested_actions=[
                    "Assign a surgeon with appropriate specialization",
                    "Verify surgeon qualifications",
                    "Consider supervision if allowed"
                ]
            )
            violations.append(violation)

        return violations

    def _check_custom_constraints(
        self,
        surgery: Surgery,
        room_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[ConstraintViolation]:
        """Check custom constraint rules."""
        violations = []

        for rule_id, rule in self.custom_rules.items():
            if not rule.enabled:
                continue

            # Check if rule applies to this surgery
            if not self._rule_applies_to_surgery(rule, surgery, room_id):
                continue

            # Evaluate rule conditions
            violation = self._evaluate_custom_rule(rule, surgery, room_id, start_time, end_time)
            if violation:
                violations.append(violation)

        return violations

    def _rule_applies_to_surgery(
        self,
        rule: CustomConstraintRule,
        surgery: Surgery,
        room_id: int
    ) -> bool:
        """Check if a custom rule applies to the given surgery."""

        # Check surgery type applicability
        if "surgery_types" in rule.applies_to:
            if surgery.surgery_type_id not in rule.applies_to["surgery_types"]:
                return False

        # Check room applicability
        if "rooms" in rule.applies_to:
            if room_id not in rule.applies_to["rooms"]:
                return False

        # Check surgeon applicability
        if "surgeons" in rule.applies_to and surgery.surgeon_id:
            if surgery.surgeon_id not in rule.applies_to["surgeons"]:
                return False

        return True

    def _evaluate_custom_rule(
        self,
        rule: CustomConstraintRule,
        surgery: Surgery,
        room_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[ConstraintViolation]:
        """Evaluate a custom constraint rule."""

        # This is a simplified implementation
        # In practice, this would use a more sophisticated rule engine

        if rule.rule_type == "time_based":
            return self._evaluate_time_based_rule(rule, surgery, start_time, end_time)
        elif rule.rule_type == "resource_based":
            return self._evaluate_resource_based_rule(rule, surgery, room_id)
        elif rule.rule_type == "duration_based":
            return self._evaluate_duration_based_rule(rule, surgery, start_time, end_time)

        return None

    def _evaluate_time_based_rule(
        self,
        rule: CustomConstraintRule,
        surgery: Surgery,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[ConstraintViolation]:
        """Evaluate time-based custom rule."""

        conditions = rule.conditions

        # Check time window restrictions
        if "allowed_hours" in conditions:
            allowed_start = conditions["allowed_hours"].get("start", "00:00")
            allowed_end = conditions["allowed_hours"].get("end", "23:59")

            start_hour = start_time.strftime("%H:%M")
            end_hour = end_time.strftime("%H:%M")

            if start_hour < allowed_start or end_hour > allowed_end:
                return ConstraintViolation(
                    constraint_id=f"custom_time_window_{rule.rule_id}",
                    constraint_type=ConstraintType.TIME_WINDOW,
                    severity=ConstraintSeverity.MEDIUM,
                    description=f"Surgery scheduled outside allowed time window ({allowed_start}-{allowed_end})",
                    surgery_id=surgery.surgery_id,
                    start_time=start_time,
                    end_time=end_time,
                    suggested_actions=[
                        f"Schedule surgery between {allowed_start} and {allowed_end}",
                        "Request exception approval"
                    ]
                )

        # Check day of week restrictions
        if "allowed_days" in conditions:
            allowed_days = conditions["allowed_days"]
            surgery_day = start_time.strftime("%A")

            if surgery_day not in allowed_days:
                return ConstraintViolation(
                    constraint_id=f"custom_day_restriction_{rule.rule_id}",
                    constraint_type=ConstraintType.TIME_WINDOW,
                    severity=ConstraintSeverity.MEDIUM,
                    description=f"Surgery scheduled on restricted day ({surgery_day})",
                    surgery_id=surgery.surgery_id,
                    start_time=start_time,
                    suggested_actions=[
                        f"Schedule surgery on allowed days: {', '.join(allowed_days)}",
                        "Request exception approval"
                    ]
                )

        return None

    def _evaluate_resource_based_rule(
        self,
        rule: CustomConstraintRule,
        surgery: Surgery,
        room_id: int
    ) -> Optional[ConstraintViolation]:
        """Evaluate resource-based custom rule."""

        conditions = rule.conditions

        # Check room restrictions
        if "restricted_rooms" in conditions:
            restricted_rooms = conditions["restricted_rooms"]
            if room_id in restricted_rooms:
                return ConstraintViolation(
                    constraint_id=f"custom_room_restriction_{rule.rule_id}",
                    constraint_type=ConstraintType.RESOURCE_CONFLICT,
                    severity=ConstraintSeverity.HIGH,
                    description=f"Surgery assigned to restricted room {room_id}",
                    surgery_id=surgery.surgery_id,
                    room_id=room_id,
                    suggested_actions=[
                        "Choose an unrestricted room",
                        "Request exception approval"
                    ]
                )

        return None

    def _evaluate_duration_based_rule(
        self,
        rule: CustomConstraintRule,
        surgery: Surgery,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[ConstraintViolation]:
        """Evaluate duration-based custom rule."""

        conditions = rule.conditions
        duration_minutes = (end_time - start_time).total_seconds() / 60

        # Check maximum duration
        if "max_duration_minutes" in conditions:
            max_duration = conditions["max_duration_minutes"]
            if duration_minutes > max_duration:
                return ConstraintViolation(
                    constraint_id=f"custom_max_duration_{rule.rule_id}",
                    constraint_type=ConstraintType.CUSTOM,
                    severity=ConstraintSeverity.MEDIUM,
                    description=f"Surgery duration ({duration_minutes:.0f} min) exceeds maximum allowed ({max_duration} min)",
                    surgery_id=surgery.surgery_id,
                    start_time=start_time,
                    end_time=end_time,
                    suggested_actions=[
                        f"Reduce surgery duration to {max_duration} minutes or less",
                        "Split surgery into multiple sessions",
                        "Request exception approval"
                    ]
                )

        # Check minimum duration
        if "min_duration_minutes" in conditions:
            min_duration = conditions["min_duration_minutes"]
            if duration_minutes < min_duration:
                return ConstraintViolation(
                    constraint_id=f"custom_min_duration_{rule.rule_id}",
                    constraint_type=ConstraintType.CUSTOM,
                    severity=ConstraintSeverity.LOW,
                    description=f"Surgery duration ({duration_minutes:.0f} min) is below minimum recommended ({min_duration} min)",
                    surgery_id=surgery.surgery_id,
                    start_time=start_time,
                    end_time=end_time,
                    suggested_actions=[
                        f"Increase surgery duration to at least {min_duration} minutes",
                        "Verify surgery requirements"
                    ]
                )

        return None

    def _generate_recommendations(
        self,
        violations: List[ConstraintViolation],
        surgery: Surgery
    ) -> List[str]:
        """Generate recommendations based on constraint violations."""
        recommendations = []

        # Count violations by type
        violation_counts = {}
        for violation in violations:
            violation_type = violation.constraint_type
            violation_counts[violation_type] = violation_counts.get(violation_type, 0) + 1

        # Generate type-specific recommendations
        if ConstraintType.EQUIPMENT_AVAILABILITY in violation_counts:
            recommendations.append("Review equipment requirements and availability")
            recommendations.append("Consider alternative equipment or time slots")

        if ConstraintType.STAFF_AVAILABILITY in violation_counts:
            recommendations.append("Review staff assignments and availability")
            recommendations.append("Consider alternative staff or scheduling")

        if ConstraintType.SURGEON_SPECIALIZATION in violation_counts:
            recommendations.append("Verify surgeon qualifications for this surgery type")
            recommendations.append("Consider assigning a more specialized surgeon")

        if ConstraintType.RESOURCE_CONFLICT in violation_counts:
            recommendations.append("Resolve resource conflicts by adjusting schedule")
            recommendations.append("Consider using alternative resources")

        if ConstraintType.TIME_WINDOW in violation_counts:
            recommendations.append("Adjust surgery timing to comply with time restrictions")
            recommendations.append("Request approval for time window exceptions")

        # General recommendations
        if len(violations) > 3:
            recommendations.append("Consider rescheduling surgery to a more suitable time")

        if any(v.severity == ConstraintSeverity.CRITICAL for v in violations):
            recommendations.append("Address critical violations before proceeding")

        return recommendations

    def add_constraint_configuration(self, config: ConstraintConfiguration):
        """Add or update a constraint configuration."""
        self.constraint_configurations[config.constraint_id] = config
        logger.info(f"Added constraint configuration: {config.constraint_id}")

    def remove_constraint_configuration(self, constraint_id: str) -> bool:
        """Remove a constraint configuration."""
        if constraint_id in self.constraint_configurations:
            del self.constraint_configurations[constraint_id]
            logger.info(f"Removed constraint configuration: {constraint_id}")
            return True
        return False

    def add_custom_rule(self, rule: CustomConstraintRule):
        """Add or update a custom constraint rule."""
        self.custom_rules[rule.rule_id] = rule
        logger.info(f"Added custom rule: {rule.rule_id}")

    def remove_custom_rule(self, rule_id: str) -> bool:
        """Remove a custom constraint rule."""
        if rule_id in self.custom_rules:
            del self.custom_rules[rule_id]
            logger.info(f"Removed custom rule: {rule_id}")
            return True
        return False

    def get_constraint_configurations(self) -> List[ConstraintConfiguration]:
        """Get all constraint configurations."""
        return list(self.constraint_configurations.values())

    def get_custom_rules(self) -> List[CustomConstraintRule]:
        """Get all custom constraint rules."""
        return list(self.custom_rules.values())

    def validate_schedule_constraints(
        self,
        assignments: List[SurgeryRoomAssignment]
    ) -> Dict[str, Any]:
        """Validate constraints for an entire schedule."""

        all_violations = []
        all_warnings = []
        feasible_count = 0
        total_count = len(assignments)

        for assignment in assignments:
            request = FeasibilityCheckRequest(
                surgery_id=assignment.surgery_id,
                room_id=assignment.room_id,
                start_time=assignment.start_time,
                end_time=assignment.end_time,
                current_assignments=[{
                    'surgery_id': a.surgery_id,
                    'room_id': a.room_id,
                    'start_time': a.start_time,
                    'end_time': a.end_time
                } for a in assignments if a.surgery_id != assignment.surgery_id]
            )

            result = self.check_feasibility_advanced(request)

            if result.is_feasible:
                feasible_count += 1

            all_violations.extend(result.violations)
            all_warnings.extend(result.warnings)

        return {
            'total_surgeries': total_count,
            'feasible_surgeries': feasible_count,
            'feasibility_rate': feasible_count / total_count if total_count > 0 else 1.0,
            'total_violations': len(all_violations),
            'critical_violations': len([v for v in all_violations if v.severity == ConstraintSeverity.CRITICAL]),
            'violations_by_type': self._group_violations_by_type(all_violations),
            'recommendations': self._generate_schedule_recommendations(all_violations)
        }

    def _group_violations_by_type(self, violations: List[ConstraintViolation]) -> Dict[str, int]:
        """Group violations by constraint type."""
        grouped = {}
        for violation in violations:
            constraint_type = violation.constraint_type.value
            grouped[constraint_type] = grouped.get(constraint_type, 0) + 1
        return grouped

    def _generate_schedule_recommendations(self, violations: List[ConstraintViolation]) -> List[str]:
        """Generate recommendations for schedule-level violations."""
        recommendations = []

        violation_counts = self._group_violations_by_type(violations)

        if violation_counts.get('equipment_availability', 0) > 0:
            recommendations.append("Review equipment allocation across all surgeries")

        if violation_counts.get('staff_availability', 0) > 0:
            recommendations.append("Optimize staff assignments to reduce conflicts")

        if violation_counts.get('surgeon_specialization', 0) > 0:
            recommendations.append("Review surgeon-surgery type assignments")

        if len(violations) > len(violations) * 0.2:  # More than 20% violations
            recommendations.append("Consider major schedule restructuring")

        return recommendations