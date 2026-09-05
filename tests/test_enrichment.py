"""
Automated Pytest for verifiable-delay-function-vdf Enrichment Modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from enrichment import (
    PerformanceBenchmarkingSuiteWithOperationCountsAndTimingEngine,
    SidechannelResistanceAnalysisConstanttimeVerificationEngine,
    InteroperabilityTestingAgainstLiboqsPqcryptoBoringsslVectorsEngine,
    VdfScalabilityAnalyzerSequentialTimeVsProofSizeEngine,
    FormalSecurityProofDocumentationSequentialSquaringAssumptionEngine,
    NistComplianceCertificationChecklistWithTestVectorValidationEngine,
    AdditionalEnhancementBlockchainVdfSimulatorEngine,
    AdditionalEnhancementParallelVerificationOptimizerEngine,
    VerifiabledelayfunctionvdfEnrichmentSuite,
    enrichment_suite,
)

def test_enrichment_suite_execution():
    suite = VerifiabledelayfunctionvdfEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    assert len(res) >= 1
    for k, v in res.items():
        assert v.status in ["OPTIMAL", "WARNING", "CRITICAL_ALERT"]
        assert isinstance(v.recommendations, list)

def test_enrichment_threshold_escalation():
    suite = VerifiabledelayfunctionvdfEnrichmentSuite()
    res = suite.execute_all(primary_val=10.0, secondary_val=5.0)
    for k, v in res.items():
        assert v.status in ["WARNING", "CRITICAL_ALERT"]
        assert len(v.alerts) > 0


def test_enrichment_suite_all_engines_executed():
    """Verify all 8 enrichment engines produce distinct results (bug fix for duplicate assignment)."""
    suite = VerifiabledelayfunctionvdfEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    assert len(res) == 8, f"Expected 8 engines, got {len(res)}"
    # Verify both blockchain and parallel engines are present and independent
    assert "AdditionalEnhancementBlockchainVdfSimulatorEngine" in res
    assert "AdditionalEnhancementParallelVerificationOptimizerEngine" in res
    # Verify the suite has both attributes (not overwritten)
    assert hasattr(suite, "blockchainvdfsimul")
    assert hasattr(suite, "parallelverificatio")
    assert suite.blockchainvdfsimul is not suite.parallelverificatio
