from __future__ import annotations

from tri.external_public_annotation import redact_sensitive


def test_redacts_nested_credentials_but_preserves_entity_ids() -> None:
    source = {
        "password": "unsafe",
        "session_token": "unsafe-token",
        "events": [
            {
                "event_id": "E-1",
                "details": {"api_key": "unsafe-key", "name": "Planning"},
            }
        ],
    }
    redacted = redact_sensitive(source)
    assert redacted["password"] == "<REDACTED>"
    assert redacted["session_token"] == "<REDACTED>"
    assert redacted["events"][0]["details"]["api_key"] == "<REDACTED>"
    assert redacted["events"][0]["event_id"] == "E-1"
    assert redacted["events"][0]["details"]["name"] == "Planning"
