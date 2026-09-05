"""
Pydantic v2 schemas and data definitions for Verifiable Delay Function Vdf.
Domain: Post-Quantum Cryptography & Hardware Security
Standard: NIST FIPS 203/204/205 / ISO/IEC 17825 Standards
"""
import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., description="Unique task / case identifier", min_length=1, max_length=128)
    target_identifier: str = Field(..., description="Entity, patient key, or genomic/cryptographic target", min_length=1, max_length=128)
    primary_metric: float = Field(..., description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", description="Status code or phenotype descriptor", max_length=64)
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("task_id", "target_identifier")
    @classmethod
    def validate_identifiers(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Identifier fields must not be empty or whitespace-only")
        # Prevent path traversal and injection characters
        forbidden_chars = {"..", "//", "\\", "\x00", "\n", "\r", "\t"}
        for ch in forbidden_chars:
            if ch in v:
                raise ValueError(f"Identifier contains forbidden character sequence: {repr(ch)}")
        return v.strip()

    @field_validator("primary_metric", "secondary_metric")
    @classmethod
    def validate_metrics(cls, v: float) -> float:
        if not isinstance(v, (int, float)):
            raise ValueError("Metric values must be numeric")
        if (-1e6) > v or v > 1e6:
            raise ValueError("Metric value out of acceptable bounds (-1e6 to 1e6)")
        return float(v)


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "NIST FIPS 203/204/205 / ISO/IEC 17825 Standards"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "verifiable-delay-function-vdf"
    domain: str = "Post-Quantum Cryptography & Hardware Security"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "NIST FIPS 203/204/205 / ISO/IEC 17825 Standards"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
