"""Input, CSV, and audit-log safety regressions."""
import math
import pytest

from agents.base import AuditTrail
from agents.models import SystemTaskPayload
from cli import parse_csv_bool as parse_primary_bool
from vdf_engine.cli import parse_csv_bool as parse_legacy_bool


@pytest.mark.parametrize("parse", [parse_primary_bool, parse_legacy_bool])
@pytest.mark.parametrize("value,expected", [
    ("True", True), (" true ", True), ("1", True), ("yes", True),
    ("False", False), ("0", False), ("no", False), ("", False),
])
def test_boolean_csv_values(parse, value, expected):
    assert parse(value) is expected


@pytest.mark.parametrize("parse", [parse_primary_bool, parse_legacy_bool])
def test_bad_csv_bool_rejected(parse):
    with pytest.raises(ValueError):
        parse("maybe")


@pytest.mark.parametrize("nonfinite", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_metric_rejected(nonfinite):
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="T", target_identifier="X", primary_metric=nonfinite)


def test_audit_trail_is_defensive_copy():
    audit = AuditTrail("test-key")
    audit.log("tester", "worker", "RUN", {"status":"OK"})
    returned = audit.get_trail()
    returned[0]["current_hash"] = "spoofed"
    returned.clear()
    assert len(audit.get_trail()) == 1
    assert audit.verify_integrity()
