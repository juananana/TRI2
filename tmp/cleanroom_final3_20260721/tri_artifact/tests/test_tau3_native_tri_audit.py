from scripts.audit_tau3_native_tri_opportunities import has_metadata_strict_candidate


def _action(requestor: str, name: str, **arguments: str) -> dict:
    return {"requestor": requestor, "name": name, "arguments": arguments}


def _task(*task_actions: dict) -> dict:
    return {"evaluation_criteria": {"actions": list(task_actions)}}


def test_screen_requires_user_transition_with_stable_id() -> None:
    task = _task(
        _action("assistant", "inspect", line_id="L1"),
        _action("user", "toggle_data"),
        _action("assistant", "mutate", line_id="L1"),
    )
    assert not has_metadata_strict_candidate(task)


def test_screen_requires_same_id_before_and_after_transition() -> None:
    task = _task(
        _action("assistant", "inspect", line_id="L1"),
        _action("user", "change", line_id="L1"),
        _action("assistant", "mutate", line_id="L2"),
    )
    assert not has_metadata_strict_candidate(task)


def test_screen_admits_same_role_post_binding_candidate() -> None:
    task = _task(
        _action("assistant", "inspect", line_id="L1"),
        _action("user", "change", line_id="L1"),
        _action("assistant", "mutate", line_id="L1"),
    )
    assert has_metadata_strict_candidate(task)
