# Review checklist — architecture and interfaces

The minimum questions for reviewing changes to `docs/architecture.md`, interfaces, deployment and configuration, and the author's guideline before writing it (S44-D8). The open mandate comes first: these questions are a floor, not the limit of the review. Each question names its source in [research.md](../slices/poc-4-4-stage-checklists/research.md).

## Questions

1. For every data flow the change adds or alters: which trust boundary does it cross, and does the architecture show that boundary? [S:owasp-threat]
2. Does any component gain access to a key, secret, socket or token it is not a holder of in `security/invariants.yaml`? [S:stride]
3. Can a caller without the privilege reach a privileged action through the new or changed interface? [S:stride]
4. Can a caller pass for another identity, or tamper with data, across the interface? [S:stride]
5. Does every threat the change opens have a response in the design? [S:owasp-threat]
6. Do the architecture's text and diagrams reflect the system as built: no component, flow or store missing or stale? [S:owasp-threat]
7. Which quality attributes does the decision trade off (security, availability, modifiability), and are the risks named? [S:atam]
8. Does each enforcement decision leave an audit trace that shows who did what? [S:stride]
9. When a dependency fails or answers late, does the interface deny by default? [S:owasp-code-review]
10. Is every piece of state a decision depends on written down: its store, writer, reader, lifetime and whether it is authoritative? [S:owasp-threat]

## Blocks at this stage

Besides the blocking criteria of every stage (`AGENTS.md`, Review findings), a finding blocks here when:

- the design lets an asset reach a non-holder;
- a trust boundary is crossed without verifying the caller;
- a fail-open path in a security decision;
- the design contradicts a requirement or the threat model.
