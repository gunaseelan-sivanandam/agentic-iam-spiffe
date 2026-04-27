# DDR

## Design decision
- Implement one shared shell-level verified HTTPS request helper and route the existing harness/demo request helpers through it instead of keeping multiple ad hoc request implementations.

## Alternatives considered
- Option A: inline `openssl s_client` logic at every call site
  - pros
    - no helper indirection
  - cons
    - duplicated parsing and timeout logic
    - high drift and maintenance risk
- Option B: keep current helper names but replace their internals with one verified request path
  - pros
    - smaller surface-area change for test cases
    - centralizes verification behavior
  - cons
    - helper internals become more complex
- Option C: add a Python helper script for verified requests
  - pros
    - easier structured parsing
  - cons
    - larger tooling dependency surface
    - less aligned with the current shell harness style

## Chosen option
- Option B.
- Keep the existing helper entry points where useful, but replace their internals with a single verified-request implementation so call-site churn stays limited and verification semantics stay centralized.

## Rejected options
- Option A was rejected due to duplication and drift risk.
- Option C was rejected because the harness already operates in shell and this slice does not require a new language/runtime dependency.
