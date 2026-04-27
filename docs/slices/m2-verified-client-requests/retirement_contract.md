# Retirement Contract

## Logic to remove
- Dead code:
  - none expected yet; helper internals are the primary target
- Duplicated logic superseded by shared code:
  - ad hoc repeated `curl --insecure` request execution in normal HTTPS helper paths
  - ad hoc repeated IP rewrite plus `Host:` header handling for verified request execution
- Compatibility shortcuts to retire:
  - `--insecure` in ordinary HTTPS request proof paths

## Artifact cleanup
- Stale docs/spec rows to remove:
  - wording that implies `--insecure` request execution is acceptable proof of verified service identity
- Stale tests/helpers to remove:
  - helper behavior that rewrites to resolved IPs for final verified HTTPS execution
- Unnecessary generated or checked-in artifacts to delete or archive:
  - none expected in this slice

## Deferred retention
- Coarse readiness helpers such as `wait_dns`, `wait_tcp`, and any non-proof HTTP readiness checks may remain if they are clearly kept as readiness gates rather than identity-proof mechanisms.
- Existing explicit negative TLS tests may remain as complementary proof and regression coverage unless implementation shows they are redundant.
