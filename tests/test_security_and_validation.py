"""
Security and Input Validation Tests for verifiable-delay-function-vdf.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditTrail, AuditLogger, SecurityException, assert_no_phi
from agents.models import SystemTaskPayload


class TestPHIGuard:
    """Tests for PHI outbound guard functionality."""

    def test_phi_guard_blocks_mrn(self):
        with pytest.raises(SecurityException) as exc_info:
            PHIGuard.assert_no_phi("Patient MRN-12345678")
        # Ensure error message does NOT expose regex pattern
        assert "pattern" not in str(exc_info.value).lower()
        assert "Sensitive identifier detected" in str(exc_info.value)

    def test_phi_guard_blocks_ssn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phi_guard_blocks_phone(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call 555-123-4567")

    def test_phi_guard_blocks_email(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email: user@example.com")

    def test_phi_guard_blocks_dob(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("DOB: 01/15/1990")

    def test_phi_guard_blocks_patient_name(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient Name: John Smith")

    def test_phi_guard_allows_clean_text(self):
        PHIGuard.assert_no_phi("Analytical specimen KEY-001 optimal")
        PHIGuard.assert_no_phi("Task evaluation complete")
        PHIGuard.assert_no_phi("")

    def test_phi_guard_handles_none_and_empty(self):
        PHIGuard.assert_no_phi("")
        PHIGuard.assert_no_phi(None)

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Contact user@example.com for MRN-12345")
        assert "user@example.com" not in result
        assert "MRN-12345" not in result
        assert "[REDACTED_IDENTIFIER]" in result

    def test_module_level_assert_no_phi(self):
        with pytest.raises(SecurityException):
            assert_no_phi("SSN 123-45-6789")
        assert_no_phi("clean text")


class TestAuditTrail:
    """Tests for HMAC-SHA256 audit trail integrity."""

    def test_audit_trail_generates_random_key_by_default(self):
        trail = AuditTrail()
        assert len(trail.secret_key) == 32  # 256-bit key

    def test_audit_trail_accepts_custom_key(self):
        trail = AuditTrail(secret_key="my-custom-key")
        assert trail.secret_key == b"my-custom-key"

    def test_audit_trail_logs_and_verifies(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("test_actor", "tier1", "TEST_EVENT", {"data": "value"})
        assert len(trail.get_trail()) == 1
        assert trail.verify_integrity() is True

    def test_audit_trail_chain_integrity(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("actor1", "tier1", "EVENT_1", {"step": 1})
        trail.log("actor2", "tier1", "EVENT_2", {"step": 2})
        trail.log("actor3", "tier1", "EVENT_3", {"step": 3})
        assert len(trail.get_trail()) == 3
        assert trail.verify_integrity() is True

    def test_audit_trail_detects_tampering(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("actor1", "tier1", "EVENT_1", {"step": 1})
        trail.log("actor2", "tier1", "EVENT_2", {"step": 2})
        # Tamper with the first entry
        trail.logs[0]["payload_hash"] = "tampered_hash"
        assert trail.verify_integrity() is False

    def test_audit_trail_detects_signature_tampering(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("actor1", "tier1", "EVENT_1", {"step": 1})
        # Tamper with the signature
        trail.logs[0]["current_hash"] = "invalid_signature"
        assert trail.verify_integrity() is False

    def test_audit_trail_empty_is_valid(self):
        trail = AuditTrail()
        assert trail.verify_integrity() is True
        assert trail.get_trail() == []


class TestInputValidation:
    """Tests for input validation on SystemTaskPayload."""

    def test_valid_payload(self):
        payload = SystemTaskPayload(
            task_id="TASK-001",
            target_identifier="KEY-001",
            primary_metric=25.0,
            secondary_metric=10.0,
        )
        assert payload.task_id == "TASK-001"
        assert payload.primary_metric == 25.0

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="",
                target_identifier="KEY-001",
                primary_metric=10.0,
            )

    def test_whitespace_only_task_id_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="   ",
                target_identifier="KEY-001",
                primary_metric=10.0,
            )

    def test_path_traversal_in_task_id_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="../../../etc/passwd",
                target_identifier="KEY-001",
                primary_metric=10.0,
            )

    def test_null_byte_in_task_id_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="task\x00malicious",
                target_identifier="KEY-001",
                primary_metric=10.0,
            )

    def test_metric_out_of_bounds_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="TASK-001",
                target_identifier="KEY-001",
                primary_metric=1e7,
            )

    def test_negative_metric_out_of_bounds_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="TASK-001",
                target_identifier="KEY-001",
                primary_metric=-1e7,
            )

    def test_task_id_stripped(self):
        payload = SystemTaskPayload(
            task_id="  TASK-001  ",
            target_identifier="KEY-001",
            primary_metric=10.0,
        )
        assert payload.task_id == "TASK-001"

    def test_status_descriptor_max_length(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(
                task_id="TASK-001",
                target_identifier="KEY-001",
                primary_metric=10.0,
                status_descriptor="A" * 100,
            )
