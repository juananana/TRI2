from __future__ import annotations

import re
from typing import Any


ROLE_REGISTRY_VERSION = "TRI-private-human-role-registry-v1"
TOKEN_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_private_role_registry(
    registry: dict[str, Any], required_roles: tuple[str, ...]
) -> dict[str, str]:
    """Validate pseudonymous role separation without exposing participant identity."""
    if registry.get("version") != ROLE_REGISTRY_VERSION or registry.get("status") != "locked":
        raise ValueError("private role registry is not versioned and locked")
    if (
        registry.get("token_policy")
        != "stable-per-person-random-128-bit-minimum-hashed-sha256"
        or registry.get("one_token_per_natural_person") is not True
        or registry.get("coordinator_verified_no_role_overlap") is not True
    ):
        raise ValueError("private role registry token policy is invalid")
    roles = registry.get("roles")
    if not isinstance(roles, dict) or not set(required_roles) <= set(roles):
        raise ValueError(f"private role registry requires roles: {', '.join(required_roles)}")
    hashes: dict[str, str] = {}
    for role in required_roles:
        item = roles.get(role)
        value = item.get("participant_token_sha256") if isinstance(item, dict) else None
        if not isinstance(value, str) or TOKEN_SHA256_RE.fullmatch(value) is None:
            raise ValueError(f"private role registry has invalid token hash for {role}")
        hashes[role] = value
    if len(set(hashes.values())) != len(hashes):
        raise ValueError("private role registry contains a cross-role participant overlap")
    return hashes
