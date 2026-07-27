from pathlib import Path

from tri.public_audit_sensitivity import FEATURES, build_controls, build_report, strict_label


ROOT = Path(__file__).resolve().parents[1]


def test_strict_label_requires_every_feature():
    values = {feature: True for feature in FEATURES}
    assert strict_label(values)
    values[FEATURES[3]] = False
    assert not strict_label(values)


def test_injected_sensitivity_denominators_and_labels():
    checklist = ROOT / "reports" / "benchmark_coverage_checklist.json"
    structural = ROOT / "reports" / "external_public_opportunity_audit_v1.json"
    rows = build_controls(checklist, structural)
    report = build_report(rows, checklist, structural)
    assert len(rows) == 60
    assert report["strict_positive_recall"] == {"numerator": 30, "denominator": 30}
    assert report["hard_negative_exclusion"] == {"numerator": 30, "denominator": 30}
    assert "does not estimate recall" in report["boundary"]
