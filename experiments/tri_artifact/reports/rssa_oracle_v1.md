# R-SSA Zero-API Oracle and Leakage Audit

- Manifest: `data/temporal_referent_method_upgrade_smoke_v1.jsonl`
- Manifest SHA-256: `e651f4db45275877ca09a5e70187baca6d5ee8901bf983bb1ecc3885ef879181`
- Protocol SHA-256: `6d8ee0da432b6133e7cfabd4b65ec156939ff0ffa1dc8bf07143b67fd8dbfe93`
- Frozen tasks: 20 (16 scalar; 4 multi-refresh/role)

## Coverage

| Check | Result |
|---|---:|
| Valid oracle programs | 20/20 |
| Enforced authorized target | 20/20 |
| Correct composition role inventory | 20/20 |
| Compiler payloads without forbidden fields | 20/20 |
| Grounded binding instances | 24/24 |

Binding roles: `{"action_target": 20, "monitoring_reference": 4}`

Binding epochs: `{"S0": 12, "S1": 10, "S2": 2}`

## Adversarial shadow substitution

For eligible anchored flip cases, the shadow actor is deliberately set to the refreshed
winner while Free and Enforced share the same oracle program and handles.

- Eligible cases: 7
- Free wrong writes: 7
- Enforced correct writes: 7

This establishes the implementation-level intervention only. It is not learned-model
evidence and cannot be reported as R-SSA empirical performance.
