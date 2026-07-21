from __future__ import annotations

from scripts.analyze_rssa_format_audit import audit, markdown, unwrap_single_markdown_fence


def test_single_fence_unwrap_does_not_repair_inner_json() -> None:
    assert unwrap_single_markdown_fence('```json\n{"a": 1}\n```') == ('{"a": 1}', True)
    assert unwrap_single_markdown_fence('{"a": 1}') == ('{"a": 1}', False)
    assert unwrap_single_markdown_fence('prose\n{"a": 1}') == ('prose\n{"a": 1}', False)


def test_glm_format_audit_is_complete_and_remains_post_hoc() -> None:
    report = audit()
    assert report["tasks"] == 20
    assert report["counts"]["fenced_outputs"] == 20
    assert report["counts"]["relaxed_schema_valid"] == 20
    assert report["status"].startswith("post-hoc")
    rendered = markdown(report)
    assert "does not replace the prospective 0/20" in rendered
