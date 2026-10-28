# Architecture Delta

## Responsibility changes
- `ARCH-018 agent-a` gains an explicit verified-request responsibility for runtime proof paths that originate from the demo client.
- `ARCH-019 rogue-tests Harness` gains an explicit verified-request responsibility for runtime proof paths that originate from the harness.
- `ARCH-003 Boundary-Authenticated Transport and Identity Propagation` is clarified so black-box proof of service identity requires a verified client request path, not only a verified ingress configuration.
- `ARCH-007 Evidence and Security Verification Harness` is clarified so ordinary HTTPS request evidence must come from verified request execution, not from `--insecure` shortcuts.

## Authoritative state inventory

| State / Key | Store / System | Writer | Reader | TTL / Lifecycle | Decision impact | Type |
|---|---|---|---|---|---|---|
| SPIFFE trust bundle (`bundle.pem`) | Filesystem / mounted SVID material | SPIRE agent | Harness / demo client | Rotated with SVID material | Determines whether the server trust chain is accepted | Authoritative |
| Expected service SPIFFE ID | Harness/client configuration | Harness / demo client | Harness / demo client | Process lifetime / test scope | Determines whether the request is accepted as the intended service identity | Authoritative |

## Hidden behavior disclosure
- The current harness rewrites HTTPS URLs to resolved IPs and relies on `Host:` headers while also using `--insecure`; that path is not a valid proof of server identity verification.
- The current negative TLS tests prove some handshake rejection behavior, but they do not make ordinary `--insecure` request paths semantically equivalent to verified client requests.
- This slice introduces no new shared runtime state; it changes how proof requests are executed and validated.
