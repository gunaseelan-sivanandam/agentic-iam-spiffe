# E2E Test Specification

Hand-written, plain-English description of every E2E test in `scripts/rogue_node_tests.sh`: what it tests, how it does it, and what evidence it leaves under `artifacts/rogue-tests/<test-id>_<slug>/`. Requirement mappings live in `trace/tests.yaml`. If a detail is not explicit in the harness, it is marked as UNKNOWN.

How to read it:
- Each test heading starts with its harness ID (for example `M3.S4-T2`), which is also the value to pass in `TEST_ONLY=` and the prefix of its evidence directory.
- Every test runs **premise** guards (preconditions), **exercise** guards (the action), and **outcome** guards (the assertions). A failed guard fails the test and leaves `fail_reason.txt`.
- Where a test's title claims more than its guards check, the entry says so in a note.

Maintenance rule (see `AGENTS.md`, slice workflow step 4): every change that adds or changes an E2E test updates this file in the same change. `make docs-check` fails if a harness test ID is missing here.

## Milestone 1 - Server and agent connection and successful entry

### M1-T1 — “Rogue missing join token rejects attestation”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a rogue agent attempting node attestation without a join token is rejected, and the attestation failure is recorded in the rogue’s log.

### Step‑by‑step (as implemented)

Premise guards

1. spire-server container running  
   - Confirms the SPIRE server container exists and is running.
2. spire-server resolves  
   - Resolves `spire-server`, stores its IP, and writes it to `spire_server_ip.txt`.
3. spire-server TCP reachable  
   - Verifies the SPIRE server port is reachable.
4. spire-agent container running  
   - Confirms the SPIRE agent container exists and is running.
5. agent socket present  
   - Verifies the SPIRE agent Workload API socket exists.
6. legit attestation present  
   - Confirms at least one agent is registered on the SPIRE server.
7. join token present  
   - Ensures the shared join token exists (for baseline sanity).
8. missing token file present  
   - Ensures the “missing token” file exists in `/run/spire/rogue`.

Exercise guards

1. rogue attestation attempt with missing token  
   - Runs rogue node attestation with the missing token.  
   - Output is written to `rogue_M1-T1.log`.

Outcome guards

1. attestation failed as expected  
   - Confirms the rogue log contains “Starting node attestation” and a failure signal such as “attestation failed”, “permission denied”, “invalid token”, or “join token was not provided”.

### Evidence produced

- $EVDIR/rogue_M1-T1.log  
- $EVDIR/spire_server_ip.txt  
- (non‑EVDIR) /run/spire/agent/private/api.sock  
- (non‑EVDIR) /run/spire/rogue  
- (non‑EVDIR) /run/spire/rogue/missing_token  
- (non‑EVDIR) /run/spire/server/data/private/api.sock  
- (non‑EVDIR) /run/spire/shared/join_token

### M1-T2 — “Rogue forged join token rejects attestation”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a rogue agent attesting with a forged join token is rejected, and the SPIRE server logs the attestation failure.

### Step‑by‑step (as implemented)

Premise guards

1. spire-server container running  
   - Confirms the SPIRE server container exists and is running.
2. spire-server resolves  
   - Resolves `spire-server`, stores its IP, and writes it to `spire_server_ip.txt`.
3. spire-server TCP reachable  
   - Verifies the SPIRE server port is reachable.
4. spire-agent container running  
   - Confirms the SPIRE agent container exists and is running.
5. agent socket present  
   - Verifies the SPIRE agent Workload API socket exists.
6. legit attestation present  
   - Confirms at least one agent is registered on the SPIRE server.
7. join token present  
   - Ensures the shared join token exists (for baseline sanity).
8. rogue config directory present  
   - Ensures `/run/spire/rogue` exists.

Exercise guards

1. rogue attestation attempt with forged token  
   - Generates a fake join token and attempts rogue attestation with it.  
   - Output is written to `rogue_M1-T2.log`.
2. capture spire-server attestation logs  
   - Captures recent SPIRE server logs into `spire_server.log`.

Outcome guards

1. attestation failed as expected  
   - Confirms the rogue log contains “Starting node attestation” and a failure signal such as “attestation failed”, “permission denied”, “invalid token”, or “join token does not exist”.
2. server recorded attestation failure  
   - Confirms SPIRE server logs show attestation activity and a “join token does not exist” or “has already been used” error.

### Evidence produced

- $EVDIR/rogue_M1-T2.log  
- $EVDIR/spire_server.log  
- $EVDIR/spire_server_ip.txt  
- (non‑EVDIR) /run/spire/agent/private/api.sock  
- (non‑EVDIR) /run/spire/rogue  
- (non‑EVDIR) /run/spire/rogue/fake_token  
- (non‑EVDIR) /run/spire/server/data/private/api.sock  
- (non‑EVDIR) /run/spire/shared/join_token
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/verified_capiss_result.txt
- $EVDIR/verified_capiss_spiffe_id.txt
- $EVDIR/token.txt
- $EVDIR/toolb_envoy_ip.txt
- $EVDIR/verified_toolb_result.txt
- $EVDIR/verified_toolb_spiffe_id.txt

### M1-T3 — “Rogue replayed join token rejects attestation”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a rogue agent attempting node attestation with a replayed join token is rejected, and the SPIRE server logs the attestation failure.

### Step‑by‑step (as implemented)

Premise guards

1. spire-server container running  
   - Confirms the SPIRE server container exists and is running.
2. spire-server resolves  
   - Resolves `spire-server`, stores its IP, and writes it to `spire_server_ip.txt`.
3. spire-server TCP reachable  
   - Verifies the SPIRE server port is reachable.
4. spire-agent container running  
   - Confirms the SPIRE agent container exists and is running.
5. agent socket present  
   - Verifies the SPIRE agent Workload API socket exists.
6. legit attestation present  
   - Confirms at least one agent is registered on the SPIRE server.
7. join token present  
   - Ensures the shared join token exists (for baseline sanity).

Exercise guards

1. rogue attestation attempt with replayed token  
   - Uses the existing join token from `/run/spire/shared/join_token` and attempts rogue attestation.  
   - Output is written to `rogue_M1-T3.log`.
2. capture spire-server attestation logs  
   - Captures recent SPIRE server logs into `spire_server.log`.

Outcome guards

1. attestation failed as expected  
   - Confirms the rogue log contains “Starting node attestation” and a failure signal such as “attestation failed”, “permission denied”, “invalid token”, or “join token does not exist”.
2. server recorded attestation failure  
   - Confirms SPIRE server logs show attestation activity and a “join token does not exist” or “has already been used” error.

### Evidence produced

- $EVDIR/rogue_M1-T3.log  
- $EVDIR/spire_server.log  
- $EVDIR/spire_server_ip.txt  
- (non‑EVDIR) /run/spire/agent/private/api.sock  
- (non‑EVDIR) /run/spire/server/data/private/api.sock  
- (non‑EVDIR) /run/spire/shared/join_token

### M1-T4 — “Rogue repeated attestation attempt is rejected”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a rogue agent attempting node attestation twice (duplicate attestation) is rejected, and the SPIRE server logs the attestation failure.

### Step‑by‑step (as implemented)

Premise guards

1. spire-server container running  
   - Confirms the SPIRE server container exists and is running.
2. spire-server resolves  
   - Resolves `spire-server`, stores its IP, and writes it to `spire_server_ip.txt`.
3. spire-server TCP reachable  
   - Verifies the SPIRE server port is reachable.
4. spire-agent container running  
   - Confirms the SPIRE agent container exists and is running.
5. agent socket present  
   - Verifies the SPIRE agent Workload API socket exists.
6. legit attestation present  
   - Confirms at least one agent is registered on the SPIRE server.
7. join token present  
   - Ensures the shared join token exists (for baseline sanity).

Exercise guards

1. rogue attestation attempt (repeat)  
   - Attempts rogue attestation using the existing join token again.  
   - Output is written to `rogue_M1-T4.log`.
2. capture spire-server attestation logs  
   - Captures recent SPIRE server logs into `spire_server.log`.

Outcome guards

1. attestation failed as expected  
   - Confirms the rogue log contains “Starting node attestation” and a failure signal such as “attestation failed”, “permission denied”, “invalid token”, or “join token does not exist”.
2. server recorded attestation failure  
   - Confirms SPIRE server logs show attestation activity and a “join token does not exist” or “has already been used” error.

### Evidence produced

- $EVDIR/rogue_M1-T4.log  
- $EVDIR/spire_server.log  
- $EVDIR/spire_server_ip.txt  
- (non‑EVDIR) /run/spire/agent/private/api.sock  
- (non‑EVDIR) /run/spire/server/data/private/api.sock  
- (non‑EVDIR) /run/spire/shared/join_token
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/token.txt
- $EVDIR/toolb_envoy_ip.txt

### M1-T5 — “Rogue without Workload API socket cannot fetch SVID”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a rogue container without access to the SPIRE Workload API socket cannot fetch an SVID, and the fetch attempt fails.

### Step‑by‑step (as implemented)

Premise guards

1. spire-agent container running  
   - Confirms the SPIRE agent container exists and is running.
2. agent socket present  
   - Verifies the SPIRE agent Workload API socket exists.
3. rogue container running  
   - Confirms the rogue test container exists and is running.
4. rogue socket not mounted  
   - Ensures the rogue container does **not** have the Workload API socket mounted.

Exercise guards

1. rogue socket fetch  
   - Attempts to fetch an SVID from the SPIRE Workload API inside the rogue container.  
   - Output is written to `rogue_socket_fetch.txt`.

Outcome guards

1. socket fetch failed  
   - Confirms the fetch attempt failed.
2. failure reason indicates no socket/permission  
   - Confirms the error message indicates no identity issued, no entries, permission denied, or missing socket.

### Evidence produced

- $EVDIR/rogue_socket_fetch.txt  
- (non‑EVDIR) /run/spire/agent/private/api.sock
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/toolb_envoy_ip.txt

## Milestone 2 - Workload identities security tests

### M2-T1 — “Rogue without SVID cannot access /secret”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a client without a valid SVID (no client certificate) cannot complete mTLS to tool‑b‑envoy, and the handshake is rejected as “missing client cert.”

### Step‑by‑step (as implemented)

Premise guards

1. tool-b material present  
   - Ensures tool‑b client material is prepared for the test.
2. tool-b bundle present  
   - Ensures the tool‑b trust bundle file exists.
3. resolve tool-b-envoy  
   - Resolves `tool-b-envoy`, stores its IP, and writes it to `toolb_envoy_ip.txt`.
4. tool-b-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. openssl without client cert  
   - Runs `openssl s_client` to tool‑b‑envoy **without** a client certificate.  
   - Records the return code to `rc.txt`.  
   - Confirms the TLS trace includes a `CertificateRequest`.

Outcome guards

1. missing client cert rejected  
   - Requires non‑zero return code.  
   - Rejects generic network errors (DNS/no route/connection refused).  
   - Confirms TLS failure matches “handshake failure”, “certificate required”, or “no peer certificate.”

### Evidence produced

- $EVDIR/rc.txt  
- $EVDIR/toolb_bundle.pem  
- $EVDIR/toolb_envoy_ip.txt

### M2-T2 — “Rogue with invalid client cert is rejected”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a client presenting an invalid client certificate is rejected by tool‑b‑envoy during mTLS.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b material present  
   - Ensures tool‑b client material is prepared for the test.
2. tool-b bundle present  
   - Ensures the tool‑b trust bundle file exists.
3. resolve tool-b-envoy  
   - Resolves `tool-b-envoy`, stores its IP, and writes it to `toolb_envoy_ip.txt`.
4. tool-b-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. openssl with invalid client cert  
   - Runs `openssl s_client` with an invalid client certificate and key.  
   - Records the return code to `rc.txt`.  
   - Confirms the TLS trace includes `CertificateRequest` and “write client certificate”.

Outcome guards

1. invalid client cert rejected  
   - Requires non‑zero return code.  
   - Rejects generic network errors (DNS/no route/connection refused).  
   - Confirms TLS failure matches “unknown ca”, “bad certificate”, or “certificate unknown”.

### Evidence produced

- $EVDIR/bad.pem  
- $EVDIR/rc.txt  
- $EVDIR/toolb_bundle.pem  
- $EVDIR/toolb_envoy_ip.txt  
- (non‑EVDIR) /tmp/toolb_material
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/token.txt
- $EVDIR/toolb_envoy_ip.txt

### M2-T3 — “Rogue with expired client cert is rejected”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a client presenting an expired client certificate is rejected by tool‑b‑envoy during mTLS.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b material present  
   - Ensures tool‑b client material is prepared for the test.
2. tool-b bundle present  
   - Ensures the tool‑b trust bundle file exists.
3. resolve tool-b-envoy  
   - Resolves `tool-b-envoy`, stores its IP, and writes it to `toolb_envoy_ip.txt`.
4. tool-b-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. openssl with expired client cert  
   - Runs `openssl s_client` with an expired client certificate and key.  
   - Records the return code to `rc.txt`.  
   - Confirms the TLS trace includes `CertificateRequest` and “write client certificate”.

Outcome guards

1. expired client cert rejected  
   - Requires non‑zero return code.  
   - Rejects generic network errors (DNS/no route/connection refused).  
   - Confirms TLS failure matches “unknown ca” or “unable to get local issuer certificate”.

### Evidence produced

- $EVDIR/exp.pem  
- $EVDIR/exp_ca.pem  
- $EVDIR/rc.txt  
- $EVDIR/toolb_bundle.pem  
- $EVDIR/toolb_envoy_ip.txt  
- (non‑EVDIR) /tmp/exp_ca.log  
- (non‑EVDIR) /tmp/exp_end.err  
- (non‑EVDIR) /tmp/toolb_material

### M2-T4 — “Rogue with wrong SPIFFE ID is rejected”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a client with a valid certificate but the wrong SPIFFE ID is rejected during mTLS to tool‑b‑envoy.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b material present  
   - Ensures tool‑b client material is prepared for the test.
2. tool-b cert present  
   - Ensures the tool‑b certificate file exists.
3. tool-b key present  
   - Ensures the tool‑b private key file exists.
4. tool-b bundle present  
   - Ensures the tool‑b trust bundle file exists.
5. resolve tool-b-envoy  
   - Resolves `tool-b-envoy`, stores its IP, and writes it to `toolb_envoy_ip.txt`.
6. tool-b-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. openssl with wrong SPIFFE ID  
   - Runs `openssl s_client` with tool‑b cert/key to present the wrong SPIFFE ID.  
   - Records the return code to `rc.txt`.  
   - Confirms the TLS trace includes `CertificateRequest` and “write client certificate”.

Outcome guards

1. wrong SPIFFE ID rejected  
   - Requires non‑zero return code.  
   - Rejects generic network errors (DNS/no route/connection refused).  
   - Confirms TLS failure matches “bad certificate”, “certificate unknown”, or “handshake failure”.

### Evidence produced

- $EVDIR/rc.txt  
- $EVDIR/toolb_bundle.pem  
- $EVDIR/toolb_cert.pem  
- $EVDIR/toolb_envoy_ip.txt
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/token.txt
- $EVDIR/toolb_envoy_ip.txt

### M2-T5 — “Rogue without Workload API socket cannot fetch SVID”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a rogue container without access to the SPIRE Workload API socket cannot fetch an SVID, and the fetch attempt fails.

### Step‑by‑step (as implemented)

Premise guards

1. start temp rogue container  
   - Starts a temporary rogue container and records its name.
2. workload socket missing  
   - Ensures the temporary container does **not** have the Workload API socket mounted.

Exercise guards

1. attempt fetch without socket  
   - Attempts to fetch an SVID inside the temporary container using the SPIRE agent API.  
   - Saves return code to `rc.txt` and output to `rogue_fetch.txt`.

Outcome guards

1. fetch denied without socket  
   - Requires non‑zero return code.  
   - Confirms no SVID file was produced.  
   - Confirms error output mentions missing socket / Workload API failure.

### Evidence produced

- $EVDIR/rc.txt  
- $EVDIR/rogue_fetch.txt  
- $EVDIR/temp_rogue_name.txt  
- (non‑EVDIR) /run/spire/agent/private/api.sock  
- (non‑EVDIR) /tmp/rogue_fetch  
- (non‑EVDIR) /tmp/rogue_svid  
- (non‑EVDIR) /tmp/rogue_svid/svid.pem
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/toolb_envoy_ip.txt

### M2-T6 — “Rogue with socket but no entry cannot fetch SVID”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a rogue container **with** the Workload API socket mounted but **without** a corresponding SPIFFE entry cannot fetch an SVID.

### Step‑by‑step (as implemented)

Premise guards

1. rogue socket container running  
   - Confirms `spiffe-rogue-socket` container is running.
2. workload socket present  
   - Confirms the Workload API socket exists inside the container.

Exercise guards

1. attempt fetch without entry  
   - Writes a minimal SPIRE agent config in the container.  
   - Attempts to fetch an SVID via the Workload API.  
   - Saves return code to `rc.txt` and output to `rogue_socket_fetch.txt`.

Outcome guards

1. fetch denied without entry  
   - Requires non‑zero return code.  
   - Confirms no SVID file was produced.  
   - Confirms error output indicates no identity issued / permission denied / unauthorized.

### Evidence produced

- $EVDIR/rc.txt  
- $EVDIR/rogue_socket_fetch.txt  
- (non‑EVDIR) /run/spire/agent/private/api.sock  
- (non‑EVDIR) /tmp/rogue_socket_fetch  
- (non‑EVDIR) /tmp/rogue_socket_min.conf  
- (non‑EVDIR) /tmp/rogue_socket_svid  
- (non‑EVDIR) /tmp/rogue_socket_svid/svid.pem

### M2-T7 — “Rogue cannot read SVIDs or keys”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a rogue container without SVID or agent data mounts cannot read SVIDs or private key material.

### Step‑by‑step (as implemented)

Premise guards

1. start temp rogue container  
   - Starts a temporary rogue container and records its name.
2. no SVID or agent data mounts  
   - Confirms the container does not mount `/run/spire/svid` or `/run/spire/agent/data`.

Exercise guards

1. attempt read of SVID and keys  
   - Attempts to read SVID cert, SVID key, agent SVID, and agent keys from the container.  
   - Saves return codes to `rcs.txt` and stderr outputs to `rogue_*` files.

Outcome guards

1. rogue cannot read SVID or keys  
   - Requires all read attempts to fail.  
   - Confirms error output indicates “No such file”, “Permission denied”, or “not found”.

### Evidence produced

- $EVDIR/rcs.txt  
- $EVDIR/rogue_node_keys.txt  
- $EVDIR/rogue_node_svid.txt  
- $EVDIR/rogue_svid_out.txt  
- $EVDIR/temp_rogue_name.txt  
- (non‑EVDIR) /run/spire/agent/data/keys.json  
- (non‑EVDIR) /run/spire/agent/data/svid.0.pem  
- (non‑EVDIR) /run/spire/agent/data  
- (non‑EVDIR) /run/spire/svid/svid.key  
- (non‑EVDIR) /run/spire/svid/svid.pem  
- (non‑EVDIR) /run/spire/svid  
- (non‑EVDIR) /tmp/rogue_node_keys  
- (non‑EVDIR) /tmp/rogue_node_svid  
- (non‑EVDIR) /tmp/rogue_svid_key  
- (non‑EVDIR) /tmp/rogue_svid_out

### M2-T8 — “No unintended SPIRE entries created”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

Attempt: capture entry list after tests. Expect: no unintended SPIRE entries.

### Step‑by‑step (as implemented)

Premise guards

1. baseline entry list exists  
   - Confirms the baseline entry list file exists before capturing the post‑test list.

Exercise guards

1. capture entry list after tests  
   - Captures the SPIRE entry list into `entries_after.txt`.

Outcome guards

1. no unintended SPIRE entries  
   - Asserts no diff between the baseline list and the post‑test list.

### Evidence produced

- $EVDIR/entries_after.txt

### M2-T9 — “Rogue with expired short-lived SVID is rejected”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a client presenting an expired short‑lived SVID is rejected during mTLS to tool‑b‑envoy.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b material present  
   - Ensures tool‑b client material is prepared for the test.
2. resolve tool-b-envoy  
   - Resolves `tool-b-envoy`, stores its IP, and writes it to `toolb_envoy_ip.txt`.
3. tool-b-envoy tcp reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. openssl with expired short-lived SVID  
   - Runs `openssl s_client` with the short‑lived SVID and key.  
   - Records the return code to `rc.txt`.  
   - Confirms the TLS trace includes a `CertificateRequest` and “write client certificate”.

Outcome guards

1. expired short-lived SVID rejected  
   - Requires non‑zero return code.  
   - Rejects generic network errors (DNS/no route/connection refused).  
   - Confirms TLS failure matches “expired”, “certificate has expired”, or “verify return code: 10”.

### Evidence produced

- $EVDIR/rc.txt  
- $EVDIR/short_bundle.pem  
- $EVDIR/short_svid.pem  
- $EVDIR/toolb_envoy_ip.txt  
- (non‑EVDIR) /run/spire/agent/bundle.pem  
- (non‑EVDIR) /run/spire/agent/private/api.sock  
- (non‑EVDIR) /run/spire/server/data/private/api.sock  
- (non‑EVDIR) /tmp/short_entry.err  
- (non‑EVDIR) /tmp/short_fetch.err  
- (non‑EVDIR) /tmp/short_svid
- (non‑EVDIR) /tmp/toolb_material

## Milestone 2.5 - Envoy ingress boundary

### M2.5-T1 — “tool-b app not reachable from edge network”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That the tool‑b application port on the app network is **not** reachable from an edge container, proving the network isolation boundary.

### Step‑by‑step (as implemented)

Premise guards

1. capture edge container context  
   - Records `hostname`, `ip route`, and `/etc/resolv.conf` into evidence.
2. pin tool-b app IP (toolb_app_net)  
   - Reads the tool‑b container’s app‑network IP and writes it to `toolb_ip.txt`.

Exercise guards

1. attempt direct tool-b app access from edge  
   - Attempts `curl http://<toolb_ip>:8080/health`.  
   - Writes return code to `rc.txt`.

Outcome guards

1. tool-b app not reachable from edge network  
   - Requires a connection‑level failure such as “Connection refused”, “timed out”, or “No route to host”.

### Evidence produced

- $EVDIR/hostname.txt  
- $EVDIR/ip_route.txt  
- $EVDIR/rc.txt  
- $EVDIR/resolv.conf  
- $EVDIR/toolb_direct.out  
- $EVDIR/toolb_ip.txt

### M2.5-T2 — “tool-b rejects missing x-spiffe-id header”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That tool‑b rejects requests missing the `x-spiffe-id` header when called directly (without Envoy injecting identity).

### Step‑by‑step (as implemented)

Premise guards

1. capture tool-b container context  
   - Captures `hostname`, `ip route`, and `/etc/resolv.conf` inside the tool‑b container.

Exercise guards

1. call tool-b directly without x-spiffe-id header  
   - Performs a direct HTTP request to `http://127.0.0.1:8080/secret` from inside the tool‑b container.  
   - Writes the HTTP status code to the output file.

Outcome guards

1. missing x-spiffe-id rejected by tool-b  
   - Requires the status code to be `401`.

### Evidence produced

- $EVDIR/toolb_context.txt  
- $EVDIR/toolb_missing_header.out
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/token.txt
- $EVDIR/toolb_envoy_ip.txt

### M2.5-T3 — “tool-b rejects mismatched x-spiffe-id header”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a token minted for agent‑a cannot be used by rogue to access tool‑b through Envoy when the `x-spiffe-id` does not match the token subject.

### Step‑by‑step (as implemented)

Premise guards

1. capture edge container context  
   - Records `hostname`, `ip route`, and `/etc/resolv.conf` into evidence.
2. tool-b-envoy reachable  
   - Ensures tool‑b‑envoy is reachable and writes its IP to `toolb_envoy_ip.txt`.
3. tool-b material available  
   - Ensures tool‑b client material is prepared for the test.
4. capiss material available  
   - Ensures capability‑issuer client material is prepared.
5. capiss-envoy reachable  
   - Ensures capiss‑envoy is reachable and writes its IP to `capiss_envoy_ip.txt`.

Exercise guards

1. mint capability as agent-a  
   - Requests a capability token as agent‑a and writes status to `mint_status.txt`.
2. call tool-b via envoy as rogue with agent-a token  
   - Uses the agent‑a token with rogue’s client certs and writes status to `status.txt`.

Outcome guards

1. mint allowed for agent-a  
   - Requires `mint_status.txt` to be `200`.
2. tool-b rejects mismatched x-spiffe-id/token sub  
   - Requires status `403` with reason `sub_mismatch`.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/hostname.txt  
- $EVDIR/ip_route.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_status.txt  
- $EVDIR/resolv.conf  
- $EVDIR/response.json  
- $EVDIR/status.txt  
- $EVDIR/token.txt  
- $EVDIR/toolb_envoy_ip.txt

## M3.S2 — OPA-gated capability minting

### M3.S2-T1 — “agent-a can mint (allowed by OPA)”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That agent‑a can successfully mint a capability through capiss‑envoy when OPA allows the request, the returned JSON includes the expected fields, and the request path records verified issuer identity evidence.

### Step‑by‑step (as implemented)

Premise guards

1. capiss material available  
   - Ensures capiss client cert/key are present.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. mint via envoy  
   - Sends a mint request through capiss‑envoy.  
   - Writes response JSON to `mint_body.json` and status to `status.txt`.
2. capture mint headers  
   - Runs a verbose curl and writes headers to `mint_headers.txt`.

Outcome guards

1. envoy handled mint request  
   - Confirms Envoy evidence is present in headers.
2. mint allowed 200  
   - Requires HTTP status 200.
3. token type biscuit  
   - Confirms `token_type == \"biscuit\"`.
4. token present  
   - Confirms a token is present.
5. issued_to is agent-a  
   - Confirms `issued_to == spiffe://varambu.org/agent-a`.
6. aud/act/res correct  
   - Confirms `aud == tool-b`, `act == read`, `res == tool-b:/secret`.
7. verified issuer identity recorded
   - Confirms the evidence records `spiffe://varambu.org/capability-issuer-envoy` and an `ok` verification result.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_headers.txt  
- $EVDIR/status.txt

### M3.S2-T2 — “rogue mint denied by policy”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a rogue client is denied by OPA policy when requesting a mint from capiss‑envoy.

### Step‑by‑step (as implemented)

Premise guards

1. capiss material available  
   - Ensures capiss client cert/key are present.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. mint via envoy (rogue)  
   - Sends the mint request using rogue client material.  
   - Writes response JSON to `mint_body.json` and status to `status.txt`.
2. capture mint headers  
   - Runs a verbose curl and writes headers to `mint_headers.txt`.

Outcome guards

1. envoy handled mint request  
   - Confirms Envoy evidence is present in headers.
2. policy denied 403  
   - Requires HTTP status 403.
3. policy deny body  
   - Confirms JSON contains `error == denied` and `reason == policy`.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_headers.txt  
- $EVDIR/status.txt
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/token.txt
- $EVDIR/toolb_envoy_ip.txt

### M3.S2-T3 — “OPA is not reachable from edge”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That the OPA service is not reachable from the edge test context (network isolation), while edge DNS/HTTP are otherwise healthy.

### Step‑by‑step (as implemented)

Premise guards

1. edge DNS resolves a known edge service  
   - Resolves an edge‑visible hostname (e.g., tool‑b‑envoy) and records evidence.
2. edge HTTP reachable  
   - Verifies a known edge‑reachable HTTP endpoint returns a successful response.

Exercise guards

1. attempt to reach OPA from edge  
   - Attempts to connect to `http://opa:8181/` (or decision path) from edge.  
   - Captures stdout/stderr to evidence.

Outcome guards

1. OPA not reachable from edge  
   - Requires failure to connect.  
   - Accepts only network‑isolation errors (connection refused, timed out, no route, or host not found with prior edge DNS success).  
   - Fails on success (HTTP 200) or harness errors.

### Evidence produced

- $EVDIR/edge_dns.txt  
- $EVDIR/edge_http.txt  
- $EVDIR/opa_unreachable.out

### M3.S2-T4 — “Fail closed when OPA is unavailable”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That minting fails closed when OPA is unavailable, returning a denial with reason `opa_unavailable`.

### Step‑by‑step (as implemented)

Premise guards

1. capiss no‑opa material available  
   - Ensures cert/key material for the no‑OPA envoy path is present.
2. no‑opa envoy resolves  
   - Resolves `capability-issuer-no-opa-envoy` and writes its IP to evidence.
3. no‑opa envoy TCP reachable  
   - Verifies the no‑OPA envoy port is reachable.

Exercise guards

1. mint via no‑OPA envoy  
   - Sends a mint request through the no‑OPA envoy.  
   - Writes response JSON to `mint_body.json` and status to `status.txt`.
2. capture mint headers  
   - Runs a verbose curl and writes headers to `mint_headers.txt`.

Outcome guards

1. envoy handled mint request  
   - Confirms Envoy evidence is present in headers.
2. opa unavailable denial  
   - Requires status 403 or 503.
3. opa unavailable body  
   - Confirms JSON contains `error == denied` and `reason == opa_unavailable`.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_headers.txt  
- $EVDIR/status.txt
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/token.txt
- $EVDIR/toolb_envoy_ip.txt

### M3.S2-T5 — “Issuer app not reachable from edge”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That the capability‑issuer **app** is not reachable directly from the edge context (only the Envoy should be reachable).

### Step‑by‑step (as implemented)

Premise guards

1. edge DNS resolves a known edge service  
   - Resolves an edge‑visible hostname (e.g., tool‑b‑envoy) and records evidence.
2. edge HTTP reachable  
   - Verifies a known edge‑reachable HTTP endpoint returns a successful response.

Exercise guards

1. attempt to reach capiss app from edge  
   - Attempts to connect directly to the capability‑issuer app endpoint from edge.  
   - Captures stdout/stderr to evidence.

Outcome guards

1. issuer app not reachable from edge  
   - Requires failure to connect.  
   - Accepts only network‑isolation errors (connection refused, timed out, no route, or host not found with prior edge DNS success).  
   - Fails on success (HTTP 200) or harness errors.

### Evidence produced

- $EVDIR/edge_dns.txt  
- $EVDIR/edge_http.txt  
- $EVDIR/issuer_unreachable.out
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/toolb_envoy_ip.txt

## M3.S3 — Biscuit minting

### M3.S3-T1 — “mint returns non-empty token”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a successful mint via capiss‑envoy returns a **non‑empty** token string.

### Step‑by‑step (as implemented)

Premise guards

1. capiss material available  
   - Ensures capiss client cert/key are present.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. mint via envoy  
   - Sends a mint request through capiss‑envoy.  
   - Writes response JSON to `mint_body.json` and status to `status.txt`.
2. capture mint headers  
   - Runs a verbose curl and writes headers to `mint_headers.txt`.

Outcome guards

1. mint allowed 200  
   - Requires HTTP status 200.
2. token present  
   - Confirms the `token` field is present and non‑empty.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_headers.txt  
- $EVDIR/status.txt

### M3.S3-T2 — “expires_at is present and in the near future”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a minted capability includes an `expires_at` value that is in the near future (short TTL).

### Step‑by‑step (as implemented)

Premise guards

1. capiss material available  
   - Ensures capiss client cert/key are present.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. mint via envoy  
   - Sends a mint request through capiss‑envoy.  
   - Writes response JSON to `mint_body.json` and status to `status.txt`.
2. capture mint headers  
   - Runs a verbose curl and writes headers to `mint_headers.txt`.

Outcome guards

1. mint allowed 200  
   - Requires HTTP status 200.
2. expires_at present and near future  
   - Confirms `expires_at` exists.  
   - Confirms `expires_at` is > now and within the expected short window.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_headers.txt  
- $EVDIR/status.txt  
- $EVDIR/time.txt
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/token.txt
- $EVDIR/toolb_envoy_ip.txt

### M3.S3-T3 — “two mints produce different tokens”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That two separate mint requests produce **different** Biscuit token strings.

### Step‑by‑step (as implemented)

Premise guards

1. capiss material available  
   - Ensures capiss client cert/key are present.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. mint via envoy (first)  
   - Sends a mint request and writes response JSON to `mint_body.json`.
2. mint via envoy (second)  
   - Sends a second mint request and writes response JSON to `mint_body2.json`.

Outcome guards

1. mint allowed 200  
   - Requires HTTP status 200 for both mints.
2. tokens are different  
   - Confirms the two token values are not equal.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_body2.json  
- $EVDIR/status.txt

## M3.S4 — tool-b enforces capability tokens

### M3.S4-T1 — “identity-only access to /secret is denied”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That tool‑b denies access to `/secret` when no capability token is provided, even though the caller has a valid identity.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool‑b and capiss is prepared.
2. tool-b-envoy resolves  
   - Resolves `tool-b-envoy` and writes its IP to `toolb_envoy_ip.txt`.
3. tool-b-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. call tool-b without token  
   - Calls `/secret` without an Authorization token.  
   - Writes response JSON to `response.json` and status to `status.txt`.

Outcome guards

1. no network/DNS errors  
   - Ensures the failure is not due to DNS or network issues.
2. deny status 401/403  
   - Requires HTTP 401 or 403.
3. reason missing_token  
   - Confirms JSON reason is `missing_token`.

### Evidence produced

- $EVDIR/response.json  
- $EVDIR/status.txt  
- $EVDIR/toolb_envoy_ip.txt

### M3.S4-T2 — “agent-a can access /secret with minted capability”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That agent‑a can mint a capability and use it to access tool‑b `/secret` successfully, and the request path records verified tool-b identity evidence.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool‑b and capiss is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the capiss‑envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy` and writes its IP to `toolb_envoy_ip.txt`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool‑b‑envoy port is reachable.

Exercise guards

1. mint via envoy  
   - Sends a mint request and writes response JSON to `mint_body.json`.
2. capture mint headers  
   - Runs a verbose curl and writes headers to `mint_headers.txt`.
3. call tool-b with token  
   - Calls `/secret` with the minted token and writes response JSON to `response.json`.

Outcome guards

1. envoy handled mint request  
   - Confirms Envoy evidence is present in headers.
2. mint allowed 200  
   - Requires HTTP status 200 for the mint call.
3. mint token present  
   - Confirms a token is present in the mint response.
4. no network/DNS errors  
   - Ensures the tool‑b call did not fail due to DNS or network issues.
5. allow status 200  
   - Requires HTTP status 200 from tool‑b.
6. secret value correct  
   - Confirms the response body contains the expected secret value.
7. verified tool-b identity recorded
   - Confirms the evidence records `spiffe://varambu.org/tool-b-envoy` and an `ok` verification result.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_headers.txt  
- $EVDIR/response.json  
- $EVDIR/status.txt  
- $EVDIR/toolb_envoy_ip.txt
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/token.txt
- $EVDIR/toolb_envoy_ip.txt

### M3.S4-T3 — “rogue cannot access /secret without token”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That rogue is denied when calling tool‑b `/secret` without a capability token.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool‑b and capiss is prepared.
2. tool-b-envoy resolves  
   - Resolves `tool-b-envoy` and writes its IP to `toolb_envoy_ip.txt`.
3. tool-b-envoy TCP reachable  
   - Verifies the tool‑b‑envoy port is reachable.

Exercise guards

1. rogue call tool-b without token  
   - Calls `/secret` as rogue without an Authorization token.  
   - Writes response JSON to `response.json` and status to `status.txt`.

Outcome guards

1. no network/DNS errors  
   - Ensures the failure is not due to DNS or network issues.
2. deny status 401/403  
   - Requires HTTP 401 or 403.

### Evidence produced

- $EVDIR/response.json  
- $EVDIR/status.txt  
- $EVDIR/toolb_envoy_ip.txt

### M3.S4-T4 — “stolen token replay by rogue is rejected (sub mismatch)”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a token minted for agent‑a cannot be used by rogue to access tool‑b; the request is rejected due to `sub_mismatch`.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool‑b and capiss is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the capiss‑envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy` and writes its IP to `toolb_envoy_ip.txt`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool‑b‑envoy port is reachable.

Exercise guards

1. mint via envoy  
   - Mints a token as agent‑a and writes response JSON to `mint_body.json`.
2. capture mint headers  
   - Runs a verbose curl and writes headers to `mint_headers.txt`.
3. rogue uses stolen token  
   - Calls tool‑b `/secret` as rogue using the agent‑a token.  
   - Writes response JSON to `response.json` and status to `status.txt`.

Outcome guards

1. envoy handled mint request  
   - Confirms Envoy evidence is present in headers.
2. mint allowed 200  
   - Requires HTTP status 200 for the mint call.
3. mint token present  
   - Confirms a token is present.
4. no network/DNS errors  
   - Ensures the tool‑b call did not fail due to DNS or network issues.
5. deny status 401/403  
   - Requires HTTP 401 or 403 from tool‑b.
6. reason sub_mismatch or invalid_token  
   - Confirms the response reason indicates sub mismatch or invalid token.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_headers.txt  
- $EVDIR/response.json  
- $EVDIR/status.txt  
- $EVDIR/toolb_envoy_ip.txt
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/token.txt
- $EVDIR/toolb_envoy_ip.txt

### M3.S4-T5 — “expired token is rejected”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That tool‑b rejects an expired capability token.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool‑b and capiss is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the capiss‑envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy` and writes its IP to `toolb_envoy_ip.txt`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool‑b‑envoy port is reachable.

Exercise guards

1. mint via envoy  
   - Mints a token as agent‑a and writes response JSON to `mint_body.json`.
2. capture mint headers  
   - Runs a verbose curl and writes headers to `mint_headers.txt`.
3. call tool-b with expired token  
   - Waits for the token to expire, then calls tool‑b `/secret` with the expired token.  
   - Writes response JSON to `response.json` and status to `status.txt`.

Outcome guards

1. envoy handled mint request  
   - Confirms Envoy evidence is present in headers.
2. mint allowed 200  
   - Requires HTTP status 200 for the mint call.
3. mint token and expires_at present  
   - Confirms a token and `expires_at` were returned.
4. no network/DNS errors  
   - Ensures the tool‑b call did not fail due to DNS or network issues.
5. deny status 401/403  
   - Requires HTTP 401 or 403.
6. reason expired  
   - Confirms JSON reason is `expired`.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_headers.txt  
- $EVDIR/response.json  
- $EVDIR/status.txt  
- $EVDIR/toolb_envoy_ip.txt
- $EVDIR/mint_body.json
- $EVDIR/mint_headers.txt
- $EVDIR/mint_request.json
- $EVDIR/mint_status.txt
- $EVDIR/response.json
- $EVDIR/status.txt
- $EVDIR/toolb_envoy_ip.txt

### M3.S4-T6 — “mint rejects missing parameters”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That the mint endpoint rejects a request body missing required fields, returning HTTP 400 with a `bad_request` error.

### Step‑by‑step (as implemented)

Premise guards

1. capiss material available  
   - Ensures capiss client cert/key are present.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. mint with empty body  
   - Sends an empty mint request body.  
   - Writes response JSON to `mint_body.json` and status to `status.txt`.
2. capture mint headers  
   - Runs a verbose curl and writes headers to `mint_headers.txt`.

Outcome guards

1. envoy handled mint request  
   - Confirms Envoy evidence is present in headers.
2. bad request 400  
   - Requires HTTP status 400.
3. bad_request body  
   - Confirms JSON contains `error == bad_request` and a field‑specific `reason` (e.g., `aud`).

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_headers.txt  
- $EVDIR/status.txt

### M3.S4-T7 — “mint denies unapproved authority request”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That the mint endpoint denies a request for unapproved authority (policy denies), returning HTTP 403 with a `policy` reason.

### Step‑by‑step (as implemented)

Premise guards

1. capiss material available  
   - Ensures capiss client cert/key are present.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. mint with unapproved authority  
   - Sends a mint request with an unapproved authority.  
   - Writes response JSON to `mint_body.json` and status to `status.txt`.
2. capture mint headers  
   - Runs a verbose curl and writes headers to `mint_headers.txt`.

Outcome guards

1. envoy handled mint request  
   - Confirms Envoy evidence is present in headers.
2. policy denied 403  
   - Requires HTTP status 403.
3. policy deny body  
   - Confirms JSON contains `error == denied` and `reason == policy`.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/mint_headers.txt  
- $EVDIR/status.txt

## Milestone 4 - Delegation chain and registry/budget enforcement

### M4-T1 — “root mint includes chain metadata”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That minting a root discovery token returns the expected chain metadata fields and canonical discovery resource.

### Step‑by‑step (as implemented)

Premise guards

1. capiss material available  
   - Ensures capability issuer client material is present.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy` and writes its IP to `capiss_envoy_ip.txt`.
3. capiss-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. mint root token for discovery  
   - Sends a mint request using the canonical search body.  
   - Writes response JSON to `mint_body.json` and status to `status.txt`.

Outcome guards

1. mint allowed 200  
   - Requires HTTP status 200.
2. metadata fields present  
   - Confirms token metadata is present, including `token`, `root_token_id`, `token_id`, `delegation_depth == 0`, and `parent_token_id == null`.
3. canonical search resource  
   - Confirms `res == tool-b:/search`.

### Evidence produced

- $EVDIR/capiss_envoy_ip.txt  
- $EVDIR/mint_body.json  
- $EVDIR/status.txt

### M4-T2 — “search writes discovery registry entries”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a root search token can call tool-b search, and discovery results are recorded in the registry for that root token.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool-b and capability issuer is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable  
   - Verifies the capability issuer envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool-b envoy port is reachable.
6. redis container running  
   - Confirms the redis container used for discovery registry state is running.

Exercise guards

1. mint root search token  
   - Mints a root discovery token.  
   - Writes mint response JSON to `root_mint.json` and status to `root_status.txt`.
2. call tool-b search with token  
   - Calls tool-b search endpoint with the root token.  
   - Writes response JSON to `search_response.json` and status to `search_status.txt`.

Outcome guards

1. root mint allowed 200  
   - Requires HTTP status 200 for root mint.
2. search allowed 200  
   - Requires HTTP status 200 for search call.
3. search returns canonical resources  
   - Confirms search includes `tool-b:/read-file:fileA`.
4. registry contains discovered fileA  
   - Confirms redis registry set for the root token contains `tool-b:/read-file:fileA`.

### Evidence produced

- $EVDIR/root_mint.json  
- $EVDIR/root_status.txt  
- $EVDIR/search_response.json  
- $EVDIR/search_status.txt

### M4-T3 — “resource mint requires registry proof”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That resource minting is denied when discovery registry proof is missing.

### Step‑by‑step (as implemented)

Premise guards

1. capiss material available  
   - Ensures capability issuer client material is present.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable  
   - Verifies the envoy port is reachable.

Exercise guards

1. mint root token for canonical secret resource  
   - Mints a root token for `tool-b:/secret`.  
   - Writes response JSON to `root_mint.json` and status to `root_status.txt`.
2. resource mint without discovery proof  
   - Attempts resource mint for `tool-b:/read-file:fileA` using the root token, without prior discovery registration.  
   - Writes response JSON to `resource_mint.json` and status to `resource_status.txt`.

Outcome guards

1. root mint allowed 200  
   - Requires HTTP status 200 for root mint.
2. resource mint denied 403  
   - Requires HTTP status 403 for resource mint.
3. registry miss reason  
   - Confirms response `reason == registry_miss`.

### Evidence produced

- $EVDIR/root_mint.json  
- $EVDIR/root_status.txt  
- $EVDIR/resource_mint.json  
- $EVDIR/resource_status.txt

### M4-T4 — “resource mint after discovery allows read-file”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That after discovery is registered, a resource token can be minted and used to read a file.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool-b and capability issuer is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable  
   - Verifies the capability issuer envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool-b envoy port is reachable.

Exercise guards

1. mint root search token  
   - Mints a root discovery token.  
   - Writes response JSON to `root_mint.json` and status to `root_status.txt`.
2. discover files via search  
   - Calls tool-b search using the root token.  
   - Writes response JSON to `search_response.json` and status to `search_status.txt`.
3. resource mint for read-file:fileA  
   - Mints a resource token scoped to `tool-b:/read-file:fileA`.  
   - Writes response JSON to `resource_mint.json` and status to `resource_status.txt`.
4. read file using resource token  
   - Calls read-file endpoint with the resource token.  
   - Writes response JSON to `read_response.json` and status to `read_status.txt`.

Outcome guards

1. root mint allowed 200  
   - Requires HTTP status 200 for root mint.
2. search allowed 200  
   - Requires HTTP status 200 for search.
3. resource mint allowed 200  
   - Requires HTTP status 200 for resource mint.
4. root token id preserved  
   - Confirms minted resource token is linked to the original root token id.
5. read allowed 200  
   - Requires HTTP status 200 for read-file.
6. returned file payload  
   - Confirms returned payload identifies `fileA`.

### Evidence produced

- $EVDIR/root_mint.json  
- $EVDIR/root_status.txt  
- $EVDIR/search_response.json  
- $EVDIR/search_status.txt  
- $EVDIR/resource_mint.json  
- $EVDIR/resource_status.txt  
- $EVDIR/read_response.json  
- $EVDIR/read_status.txt

### M4-T5 — “budget is enforced per root token”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That budget limits are enforced per root token: initial requests are allowed and the over-budget request is denied.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool-b and capability issuer is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable  
   - Verifies the capability issuer envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool-b envoy port is reachable.

Exercise guards

1. mint root token for canonical secret resource  
   - Mints a root token for `tool-b:/secret`.  
   - Writes response JSON to `root_mint.json` and status to `root_status.txt`.
2. consume budget with repeated `/secret` calls  
   - Sends 11 calls to `/secret` using the same root token.  
   - Writes per-call responses (`resp_*.json`), per-call status files (`st_*.txt`), and combined status log `statuses.txt`.

Outcome guards

1. root mint allowed 200  
   - Requires HTTP status 200 for root mint.
2. first ten requests allowed  
   - Requires status 200 for calls 1 through 10.
3. eleventh request denied  
   - Requires status 401 or 403 for call 11.
4. denied for budget  
   - Confirms call 11 response reason is `budget_exceeded`.

### Evidence produced

- $EVDIR/root_mint.json  
- $EVDIR/root_status.txt  
- $EVDIR/statuses.txt  
- $EVDIR/resp_11.json  
- $EVDIR/st_11.txt  
- $EVDIR/resp_*.json  
- $EVDIR/st_*.txt

### M4-T6 — “tampered token is denied”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a minted token with tampered bytes is rejected by tool-b rather than being accepted as a valid capability.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool-b and capability issuer is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable  
   - Verifies the capability issuer envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool-b envoy port is reachable.

Exercise guards

1. mint root token for canonical secret resource  
   - Mints a root token for `tool-b:/secret`.  
   - Writes response JSON to `root_mint.json` and status to `root_status.txt`.
2. tamper minted token bytes  
   - Rewrites the final byte of the minted token and writes the altered token into `tampered_token.txt`.
3. call tool-b `/secret` with tampered token  
   - Sends the tampered token to tool-b and writes response JSON to `tampered_response.json` and status to `tampered_status.txt`.

Outcome guards

1. root mint allowed 200  
   - Requires HTTP status 200 for the original root mint.
2. tampered token denied  
   - Requires status 401 or 403 for the tampered-token request.
3. invalid token reason  
   - Confirms the denial reason is `invalid_token`.

### Evidence produced

- $EVDIR/root_mint.json  
- $EVDIR/root_status.txt  
- $EVDIR/tampered_token.txt  
- $EVDIR/tampered_response.json  
- $EVDIR/tampered_status.txt

### M4-T7 — “depth limit is enforced on repeated delegation”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That repeated delegated resource minting is allowed up to the configured depth and then denied once the next mint would exceed the M4 depth ceiling.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool-b and capability issuer is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable  
   - Verifies the capability issuer envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool-b envoy port is reachable.

Exercise guards

1. mint root search token  
   - Mints a root discovery token.  
   - Writes response JSON to `root_mint.json` and status to `root_status.txt`.
2. discover files via search  
   - Calls tool-b search using the root token and writes `search_response.json` and `search_status.txt`.
3. mint delegated token depth 1  
   - Mints the first resource token for `tool-b:/read-file:fileA` and writes `depth1_mint.json` and `depth1_status.txt`.
4. mint delegated token depth 2  
   - Repeats resource mint using the previous delegated token and writes `depth2_mint.json` and `depth2_status.txt`.
5. mint delegated token depth 3  
   - Repeats resource mint using the previous delegated token and writes `depth3_mint.json` and `depth3_status.txt`.
6. attempt delegated token depth 4  
   - Attempts one more delegated mint using the depth-3 token and writes `depth4_mint.json` and `depth4_status.txt`.

Outcome guards

1. root mint allowed 200  
   - Requires HTTP status 200 for root mint.
2. search allowed 200  
   - Requires HTTP status 200 for search.
3. depth 1 mint allowed 200  
   - Requires HTTP status 200 for the first delegated token.
4. depth 2 mint allowed 200  
   - Requires HTTP status 200 for the second delegated token.
5. depth 3 mint allowed 200  
   - Requires HTTP status 200 for the third delegated token.
6. depth 4 mint denied 403  
   - Requires HTTP status 403 when one more delegated mint would exceed the configured ceiling.
7. depth exceeded reason  
   - Confirms the denial reason is `depth_exceeded`.

### Evidence produced

- $EVDIR/root_mint.json  
- $EVDIR/root_status.txt  
- $EVDIR/search_response.json  
- $EVDIR/search_status.txt  
- $EVDIR/depth1_mint.json  
- $EVDIR/depth1_status.txt  
- $EVDIR/depth2_mint.json  
- $EVDIR/depth2_status.txt  
- $EVDIR/depth3_mint.json  
- $EVDIR/depth3_status.txt  
- $EVDIR/depth4_mint.json  
- $EVDIR/depth4_status.txt  

### M4-T8 — “new-resource mint rate is enforced at capiss”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That `capiss` allows only the formula-derived number of new-resource mints under one root token context and denies the next new-resource mint attempt once the allowance is exhausted.

### Step‑by‑step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool-b and capability issuer is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable  
   - Verifies the capability issuer envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool-b envoy port is reachable.

Exercise guards

1. mint root search token  
   - Mints a root discovery token and writes `root_mint.json` and `root_status.txt`.
2. discover files via search  
   - Calls tool-b search using the root token and writes `search_response.json` and `search_status.txt`.
3. mint new resource fileA  
   - Requests `tool-b:/read-file:fileA` using the root token and writes `fileA_mint.json` and `fileA_status.txt`.
4. mint new resource fileB  
   - Requests `tool-b:/read-file:fileB` using the same root token and writes `fileB_mint.json` and `fileB_status.txt`.
5. mint new resource fileC  
   - Requests `tool-b:/read-file:fileC` using the same root token and writes `fileC_mint.json` and `fileC_status.txt`.
6. attempt fourth new-resource mint under same root  
   - Attempts another new-resource mint for `tool-b:/read-file:fileA` using the same root token and writes `fileA_again_mint.json` and `fileA_again_status.txt`.

Outcome guards

1. root mint allowed 200  
   - Requires HTTP status 200 for root mint.
2. search allowed 200  
   - Requires HTTP status 200 for search.
3. first three new-resource mints allowed 200  
   - Requires HTTP status 200 for fileA, fileB, and fileC new-resource mints.
4. fourth new-resource mint denied 403  
   - Requires HTTP status 403 once the formula-derived allowance is exhausted.
5. mint-rate exceeded reason  
   - Confirms the denial reason is `mint_rate_exceeded`.

### Evidence produced

- $EVDIR/root_mint.json  
- $EVDIR/root_status.txt  
- $EVDIR/search_response.json  
- $EVDIR/search_status.txt  
- $EVDIR/fileA_mint.json  
- $EVDIR/fileA_status.txt  
- $EVDIR/fileB_mint.json  
- $EVDIR/fileB_status.txt  
- $EVDIR/fileC_mint.json  
- $EVDIR/fileC_status.txt  
- $EVDIR/fileA_again_mint.json  
- $EVDIR/fileA_again_status.txt  

### M4-T9 — “allow flow emits correlatable audit events”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That one successful reduced-scope M4 `/search -> /read-file:fileA` flow leaves enough correlated audit evidence in `capability-issuer` and `tool-b` container logs to reconstruct the mint, discovery, and enforcement path by `root_token_id`, `token_id`, and `parent_token_id`.

### Step-by-step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool-b and capability issuer is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable  
   - Verifies the capability issuer envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool-b envoy port is reachable.

Exercise guards

1. record log capture start time  
   - Records a UTC timestamp to `log_since.txt` for later container-log capture.
2. mint root search token  
   - Mints a root discovery token and writes `root_mint.json` and `root_status.txt`.
3. discover files via search  
   - Calls tool-b search using the root token and writes `search_response.json` and `search_status.txt`.
4. resource mint for read-file:fileA  
   - Requests a delegated token for `tool-b:/read-file:fileA` and writes `resource_mint.json` and `resource_status.txt`.
5. read file using resource token  
   - Calls the file-read endpoint with the delegated token and writes `read_response.json` and `read_status.txt`.
6. capture capiss and tool-b logs since flow start  
   - Captures container logs since `log_since.txt` into `capiss_container.log` and `toolb_container.log`.
   - Filters event lines into `capiss_events.jsonl` and `toolb_events.jsonl`.

Outcome guards

1. root mint allowed 200  
   - Requires HTTP status 200 for root mint.
2. search allowed 200  
   - Requires HTTP status 200 for search.
3. resource mint allowed 200  
   - Requires HTTP status 200 for delegated mint.
4. read allowed 200  
   - Requires HTTP status 200 for file read.
5. capiss root mint event correlated  
   - Confirms a `capiss_mint_decision` allow event exists for the root mint with the expected `root_token_id`, `token_id`, canonical `res`, and `subject_spiffe_id`.
6. capiss delegated mint event correlated  
   - Confirms a `capiss_mint_decision` allow event exists for the delegated mint with matching `root_token_id`, `token_id`, `parent_token_id`, canonical `res`, and `delegator_spiffe_id`.
7. discovery registry write correlated  
   - Confirms a `discovery_registry_write` event exists for the same `root_token_id`, `subject_spiffe_id`, and canonical discovery endpoint `tool-b:/search`.
8. tool-b allow event correlated  
   - Confirms a `toolb_enforcement_decision` allow event exists for `/read-file/fileA` with matching `root_token_id`, `token_id`, `parent_token_id`, canonical `res`, `subject_spiffe_id`, and `delegator_spiffe_id`.

### Evidence produced

- $EVDIR/log_since.txt  
- $EVDIR/root_mint.json  
- $EVDIR/root_status.txt  
- $EVDIR/search_response.json  
- $EVDIR/search_status.txt  
- $EVDIR/resource_mint.json  
- $EVDIR/resource_status.txt  
- $EVDIR/read_response.json  
- $EVDIR/read_status.txt  
- $EVDIR/capiss_container.log  
- $EVDIR/capiss_events.jsonl  
- $EVDIR/toolb_container.log  
- $EVDIR/toolb_events.jsonl  

### M4-T10 — “deny flow emits correlatable mint audit event”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That one denied reduced-scope M4 new-resource mint flow leaves a correlated `capiss_mint_decision` deny event in issuer logs with the exact deny reason and the identifiers needed to explain the failed mint under the root token context.

### Step-by-step (as implemented)

Premise guards

1. tool-b and capiss material available  
   - Ensures client material for tool-b and capability issuer is prepared.
2. capiss-envoy resolves  
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable  
   - Verifies the capability issuer envoy port is reachable.
4. tool-b-envoy resolves  
   - Resolves `tool-b-envoy`.
5. tool-b-envoy TCP reachable  
   - Verifies the tool-b envoy port is reachable.

Exercise guards

1. record log capture start time  
   - Records a UTC timestamp to `log_since.txt` for later container-log capture.
2. mint root search token  
   - Mints a root discovery token and writes `root_mint.json` and `root_status.txt`.
3. discover files via search  
   - Calls tool-b search using the root token and writes `search_response.json` and `search_status.txt`.
4. mint new resource fileA  
   - Requests `tool-b:/read-file:fileA` and writes `fileA_mint.json` and `fileA_status.txt`.
5. mint new resource fileB  
   - Requests `tool-b:/read-file:fileB` and writes `fileB_mint.json` and `fileB_status.txt`.
6. mint new resource fileC  
   - Requests `tool-b:/read-file:fileC` and writes `fileC_mint.json` and `fileC_status.txt`.
7. attempt fourth new-resource mint under same root  
   - Attempts another new-resource mint for `tool-b:/read-file:fileA` and writes `fileA_again_mint.json` and `fileA_again_status.txt`.
8. capture capiss logs since flow start  
   - Captures issuer logs since `log_since.txt` into `capiss_container.log`.
   - Filters event lines into `capiss_events.jsonl`.

Outcome guards

1. root mint allowed 200  
   - Requires HTTP status 200 for root mint.
2. search allowed 200  
   - Requires HTTP status 200 for search.
3. first three new-resource mints allowed 200  
   - Requires HTTP status 200 for fileA, fileB, and fileC new-resource mints.
4. fourth new-resource mint denied 403  
   - Requires HTTP status 403 for the over-limit mint attempt.
5. mint-rate exceeded reason  
   - Confirms the denial reason is `mint_rate_exceeded`.
6. capiss mint-rate deny event correlated  
   - Confirms a `capiss_mint_decision` deny event exists with `reason_code=mint_rate_exceeded`, matching `root_token_id`, matching parent root-token `token_id`, canonical denied resource, `registry_hit=true`, and `delegator_spiffe_id`.

### Evidence produced

- $EVDIR/log_since.txt  
- $EVDIR/root_mint.json  
- $EVDIR/root_status.txt  
- $EVDIR/search_response.json  
- $EVDIR/search_status.txt  
- $EVDIR/fileA_mint.json  
- $EVDIR/fileA_status.txt  
- $EVDIR/fileB_mint.json  
- $EVDIR/fileB_status.txt  
- $EVDIR/fileC_mint.json  
- $EVDIR/fileC_status.txt  
- $EVDIR/fileA_again_mint.json  
- $EVDIR/fileA_again_status.txt  
- $EVDIR/capiss_container.log  
- $EVDIR/capiss_events.jsonl  

### M4-T11 — “amplified delegated mint is denied”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That a delegated mint cannot request authority broader than the parent token authority.

### Step-by-step (as implemented)

Premise guards

1. capiss material available
   - Ensures capability issuer client material is present.
2. capiss-envoy resolves
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable
   - Verifies the capability issuer envoy port is reachable.

Exercise guards

1. mint root secret token
   - Mints a root token for the canonical secret resource and writes `root_mint.json` and `root_status.txt`.
2. attempt delegated mint with amplified action
   - Attempts a delegated mint using the parent token but asks for `act=write` on `tool-b:/secret`.
   - Writes `amplified_mint.json` and `amplified_status.txt`.

Outcome guards

1. root mint allowed 200
   - Requires HTTP status 200 for the root mint.
2. amplified mint denied 403
   - Requires HTTP status 403 for the delegated mint attempt.
3. amplified authority reason
   - Confirms the denial reason is `amplified_authority`.

### Evidence produced

- $EVDIR/root_mint.json
- $EVDIR/root_status.txt
- $EVDIR/amplified_mint.json
- $EVDIR/amplified_status.txt

### M4-T12 — “wildcard delegated resource is denied”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That delegated resource mints only accept concrete canonical resources and reject wildcard resource strings.

### Step-by-step (as implemented)

Premise guards

1. capiss material available
   - Ensures capability issuer client material is present.
2. capiss-envoy resolves
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable
   - Verifies the capability issuer envoy port is reachable.

Exercise guards

1. mint root secret token
   - Mints a root token and writes `root_mint.json` and `root_status.txt`.
2. attempt delegated mint with wildcard resource
   - Attempts a delegated mint for `tool-b:/read-file:*`.
   - Writes `wildcard_mint.json` and `wildcard_status.txt`.

Outcome guards

1. root mint allowed 200
   - Requires HTTP status 200 for the root mint.
2. wildcard resource rejected 400
   - Requires HTTP status 400 for the wildcard resource request.
3. resource validation reason
   - Confirms the rejection reason is `res`.

### Evidence produced

- $EVDIR/root_mint.json
- $EVDIR/root_status.txt
- $EVDIR/wildcard_mint.json
- $EVDIR/wildcard_status.txt

### M4-T13 — “budget and registry TTLs are bounded by root expiry”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That Redis budget and discovery-registry state created under a root token cannot outlive the root token expiry.

### Step-by-step (as implemented)

Premise guards

1. tool-b and capiss material available
   - Ensures client material for tool-b and capability issuer is prepared.
2. capiss-envoy resolves
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable
   - Verifies the capability issuer envoy port is reachable.
4. tool-b-envoy resolves
   - Resolves `tool-b-envoy`.
5. tool-b-envoy TCP reachable
   - Verifies the tool-b envoy port is reachable.
6. redis container running
   - Confirms the Redis container used by the budget and registry state is running.

Exercise guards

1. mint root search token
   - Mints a root discovery token and writes `root_mint.json` and `root_status.txt`.
2. discover files via search
   - Calls tool-b search using the root token and writes `search_response.json` and `search_status.txt`.
3. capture redis TTLs
   - Captures Redis TTLs for `m4:budget:<root_token_id>` and `m4:registry:<root_token_id>`.
   - Captures the check time in `ttl_check_now.txt`.

Outcome guards

1. root mint allowed 200
   - Requires HTTP status 200 for root mint.
2. search allowed 200
   - Requires HTTP status 200 for search.
3. budget ttl bounded by root expiry
   - Requires the budget TTL to be positive and no longer than the remaining root-token lifetime.
4. registry ttl bounded by root expiry
   - Requires the registry TTL to be positive and no longer than the remaining root-token lifetime.

### Evidence produced

- $EVDIR/root_mint.json
- $EVDIR/root_status.txt
- $EVDIR/search_response.json
- $EVDIR/search_status.txt
- $EVDIR/budget_ttl.txt
- $EVDIR/registry_ttl.txt
- $EVDIR/ttl_check_now.txt

### M4-T14 — “protected request does not require capiss hot path”
(derived directly from scripts/rogue_node_tests.sh)

### What it tests

That using an already-minted resource token at tool-b does not require a live call to the capability issuer on the protected request path.

### Step-by-step (as implemented)

Premise guards

1. tool-b and capiss material available
   - Ensures client material for tool-b and capability issuer is prepared.
2. capiss-envoy resolves
   - Resolves `capability-issuer-envoy`.
3. capiss-envoy TCP reachable
   - Verifies the capability issuer envoy port is reachable.
4. tool-b-envoy resolves
   - Resolves `tool-b-envoy`.
5. tool-b-envoy TCP reachable
   - Verifies the tool-b envoy port is reachable.

Exercise guards

1. mint root search token
   - Mints a root discovery token and writes `root_mint.json` and `root_status.txt`.
2. discover files via search
   - Calls tool-b search using the root token and writes `search_response.json` and `search_status.txt`.
3. resource mint for read-file:fileA
   - Mints a resource token scoped to `tool-b:/read-file:fileA`.
   - Writes `resource_mint.json` and `resource_status.txt`.
4. stop capiss app before protected resource use
   - Stops the `spiffe-capability-issuer` app container after minting is complete.
5. read file using resource token while capiss is stopped
   - Calls `/read-file/fileA` using the already-minted resource token.
   - Writes `read_response.json` and `read_status.txt`.
6. restart capiss app after proof
   - Restarts the `spiffe-capability-issuer` app container.

Outcome guards

1. root mint allowed 200
   - Requires HTTP status 200 for root mint.
2. search allowed 200
   - Requires HTTP status 200 for search.
3. resource mint allowed 200
   - Requires HTTP status 200 for resource mint.
4. read allowed without capiss hot path
   - Requires HTTP status 200 while capiss is stopped.
5. returned file payload
   - Confirms returned payload identifies `fileA`.

### Evidence produced

- $EVDIR/root_mint.json
- $EVDIR/root_status.txt
- $EVDIR/search_response.json
- $EVDIR/search_status.txt
- $EVDIR/resource_mint.json
- $EVDIR/resource_status.txt
- $EVDIR/read_response.json
- $EVDIR/read_status.txt

## Milestone 4a - Jira project access with broad upstream credential

These tests are implemented in `scripts/rogue_node_tests.sh` as `M4A_T1_test` through `M4A_T10_test`. They prove that broad Jira/mock upstream access does not become broad agent authority: `capiss` and OPA mint only the allowed IAM project token, and `jira-tool` enforces identity, token action, project scope, budget/rate state, and upstream project verification before returning data.

### M4a-T1 — “mock upstream breadth”
Directly reads `IAM-1` and `NAS-1` from `jira-mock` to prove the upstream test data is broader than the agent's allowed project.

### M4a-T2 — “allowed mint and IAM read”
Mints `aud=jira-tool`, `act=read`, `res=jira-tool:/project:IAM` for agent-a, reads `IAM-1` through `jira-tool-envoy`, and records the verified `jira-tool-envoy` SPIFFE identity.

### M4a-T3 — “non-allowed project mint denied”
Attempts a NAS Jira root mint as agent-a and expects `403` with reason `policy`.

### M4a-T4 — “NAS read denied before upstream”
Uses an IAM read token against `NAS-1`, expects `403` with reason `project_mismatch`, and verifies the mock request log is empty.

### M4a-T5 — “rogue Jira mint denied”
Attempts an IAM Jira root mint using rogue client material and expects `403` with reason `policy`.

### M4a-T6 — “stolen Jira token denied”
Mints an IAM token as agent-a, reuses it with rogue client material, and expects `403` with reason `sub_mismatch` before upstream use.

### M4a-T7 — “Jira budget consumption”
Reads `IAM-1` once with an IAM token and verifies Redis budget remaining is `9`.

### M4a-T8 — “Jira budget exhaustion”
Performs eleven protected reads with one IAM token, expects the first ten to succeed and the eleventh to deny with `budget_exceeded`, and verifies only ten upstream calls occurred.

### M4a-T9 — “upstream project mismatch denied”
Reads the mismatch fixture `IAM-999`, expects `upstream_project_mismatch`, and verifies the mismatched upstream body is not returned.

### M4a-T10 — “Jira audit trace reconstruction”
Captures capiss and jira-tool logs after an allowed read and verifies correlated `capiss_mint_decision` and `jiratool_enforcement_decision` events.

## Milestone 4b - Jira project-scoped description write

These tests are implemented in `scripts/rogue_node_tests.sh` as `M4B_T1_test` through `M4B_T6_test`. They prove `act=write` is project-scoped read plus description replacement only. `act=read` cannot write, malformed or overbroad bodies are rejected locally, and NAS writes are denied before any upstream call.

### M4b-T1 — “allowed write update and readback”
Mints `aud=jira-tool`, `act=write`, `res=jira-tool:/project:IAM`, writes a timestamp marker to `IAM-1`, reads the issue back with the write token, and verifies the mock saw PUT then GET.

### M4b-T2 — “read token write denied”
Mints an IAM read token, attempts description PUT, and expects `403` with reason `insufficient_authority` and no mock write.

### M4b-T3 — “NAS write mint denied”
Attempts a NAS write root mint as agent-a and expects `403` with reason `policy`.

### M4b-T4 — “NAS write denied before upstream”
Uses an IAM write token against `NAS-1`, expects `403` with reason `project_mismatch`, and verifies no mock request occurred.

### M4b-T5 — “description write body shape”
Sends malformed JSON and a body containing both `description` and `summary`, expects `400` with `malformed_body` or `unsupported_fields`, and verifies no mock request occurred.

### M4b-T6 — “write audit trace reconstruction”
Mints an IAM write token, writes and reads `IAM-2`, captures capiss and jira-tool logs, and verifies correlated write mint plus jira-tool write/read allow events.

## Milestone 5 - Codex to Jira through MCP, Varambu audit, and full-chain trace

These tests are implemented in `scripts/rogue_node_tests.sh` as `M5_T1_test` through `M5_T59_test` (there is no `M5-T29`). They prove that an AI agent (Codex) reaching Jira through MCP gets only the authority it was minted, never more: the `codex-jira-mcp-adapter` turns each tool call into a capiss mint for exactly one action on one project, `jira-mcp-gateway` re-checks that capability before touching Jira, and every decision leaves evidence an auditor can follow end to end.

Shared vocabulary for this section:
- **Adapter** — `codex-jira-mcp-adapter`, an MCP server over stdio. Tests reach it through `scripts/codex_jira_mcp.sh`, which runs `docker compose exec -T` into the already-running container.
- **Mint** — a capiss root mint with `aud=jira-mcp-gateway`, `act=read_project_summary` or `act=create_story`, and `res=jira-mcp:/project:<KEY>`. OPA allows only the adapter identity, only for project `IAM`.
- **Gateway** — `jira-mcp-gateway` behind `jira-mcp-envoy:11443`, with endpoints `/mcp/jira/project-summary` and `/mcp/jira/stories`. It verifies the token, enforces project scope, payload shape, and budget, holds the only Jira credential, and calls upstream.
- **Mock** — `jira-mcp-mock`, a deterministic Jira holding more data than the agent may see (projects `IAM` and `NAS`). Test-only endpoints expose what it received: `/__test__/requests`, `/__test__/created`, `/__test__/breadth`, `/__test__/reset`, `/__test__/fail_next_create`.
- **Direct gateway call** — some tests skip the adapter and call the gateway with a token minted by the harness using the adapter's client material, to probe the gateway's own checks.

Group overview:

| Group | Tests | Proves |
| --- | --- | --- |
| Session and tool surface | M5-T1, M5-T2 | The launcher attaches to the running adapter; only two tools exist |
| Project summary | M5-T3 – M5-T6 | IAM summaries work, are filtered and bounded; NAS is refused at mint |
| Story creation | M5-T7 – M5-T15 | IAM stories work with criteria and epics; cross-project and malformed requests never reach Jira |
| Authority separation and token checks | M5-T16 – M5-T23 | The adapter cannot decide or widen authority; the gateway rejects wrong action, audience, subject, and invalid tokens |
| Boundary and secret hygiene | M5-T24 – M5-T30 | The gateway is not directly reachable; no tokens or Jira credentials leak to Codex, logs, or upstream |
| Budget | M5-T31 – M5-T35 | Per-token budgets apply to reads and creates |
| Audit events | M5-T36 – M5-T39 | Allow and deny decisions are logged; errors do not reveal what exists upstream |
| Upstream breadth | M5-T40, M5-T41 | The mock really is broader than the agent's authority |
| Varambu audit | M5-T42 – M5-T48 | The `varambu` audit files are complete, append-only, secret-free, and correctly timed |
| Full-chain trace | M5-T49 – M5-T59 | `varambu trace` joins intent, action, mint, gateway, and upstream legs into one honest chain per request |

### M5-T1 — “MCP launcher starts adapter session”

**What it tests:** The local Codex launcher attaches to the adapter that is already running, without starting or rebuilding the stack, and speaks clean MCP on stdout.

**How:**
- Premise: the adapter container is running; `scripts/codex_jira_mcp.sh` uses `docker compose exec -T` and contains no `compose … up` or `--build`.
- Exercise: send an MCP `tools/list` request through the launcher.
- Outcome: stdout is valid MCP JSON-RPC (`jsonrpc: "2.0"` with a tool list), and no diagnostic text (`codex-jira`, `adapter`, `ERROR`) is mixed into stdout — diagnostics go to stderr only.

**Evidence:** `tools.json`, `launcher.err`

### M5-T2 — “MCP tool surface is exactly Slice 1”

**What it tests:** Codex is offered exactly the two approved tools, in order, and nothing else.

**How:**
- Premise: the adapter container is running.
- Exercise: `tools/list` through the launcher.
- Outcome: the tool names are exactly `read_project_summary` and `create_story`.

**Evidence:** `tools.json`, `launcher.err`

### M5-T3 — “IAM project summary succeeds”

**What it tests:** The allowed path works end to end: an IAM summary request travels adapter → capiss → gateway → mock and returns data.

**How:**
- Premise: the M5 path is ready (capiss and adapter material present, both Envoys healthy) and the mock is reset.
- Exercise: call `read_project_summary` for `IAM` through MCP; read the mock's request log.
- Outcome: the response is `ok` for project `IAM` with at least one issue and one epic; the mock received `/rest/api/3/project/IAM/summary` stamped with the `jira-mcp-gateway` marker, so the call came through the gateway.

**Evidence:** `mcp_response.json`, `summary.json`, `mock_requests.json`, `adapter.err`

### M5-T4 — “Summary response contains only allowed fields”

**What it tests:** The summary is a curated view, not a raw Jira dump.

**How:**
- Premise: the M5 path is ready.
- Exercise: call `read_project_summary` for `IAM`.
- Outcome: the returned summary contains none of `description`, `comments`, `assignee`, `sprint`, `board`, `raw_jql`, `atlassian.net`, `Bearer`, or `token` (case-insensitive).

**Evidence:** `mcp_response.json`, `summary.json`

### M5-T5 — “Summary response is bounded”

**What it tests:** A large project cannot flood the agent: the summary is capped.

**How:**
- Premise: the mock's breadth report shows more than 75 IAM issues.
- Exercise: call `read_project_summary` for `IAM`.
- Outcome: at most 50 issues and at most 25 epics are returned.

**Evidence:** `breadth.json`, `summary.json`

### M5-T6 — “NAS project summary denies at capiss”

**What it tests:** A summary of a project the agent is not authorized for is refused at the mint, before any gateway or Jira call.

**How:**
- Premise: the M5 path is ready and the mock is reset.
- Exercise: call `read_project_summary` for `NAS`; read the mock's request log.
- Outcome: Codex receives `ok: false` with reason `mint_denied`, and the mock received no requests at all.

**Evidence:** `mcp_response.json`, `error.json`, `mock_requests.json`

### M5-T7 — “IAM story creation succeeds”

**What it tests:** The allowed write path creates exactly one story and returns only bounded metadata.

**How:**
- Premise: the M5 path is ready and the mock is reset.
- Exercise: call `create_story` for `IAM` with a summary and description; read the mock's created-stories list.
- Outcome: the response is `ok` with `project_key: IAM`, `issue_type: Story`, a key starting `IAM-`, and no raw Jira `fields` object; the mock stored exactly one story.

**Evidence:** `mcp_response.json`, `create.json`, `created.json`

### M5-T8 — “IAM story creation accepts criteria”

**What it tests:** Acceptance criteria supplied as a plain list end up inside the story description.

**How:**
- Premise: the M5 path is ready and the mock is reset.
- Exercise: call `create_story` for `IAM` with `acceptance_criteria: ["AC one", "AC two"]`.
- Outcome: the description the mock stored (Atlassian Document Format) contains the acceptance-criteria text.

**Evidence:** `mcp_response.json`, `create.json`, `created.json`

### M5-T9 — “IAM story creation accepts valid epic”

**What it tests:** A story can be linked to an epic in the same project, and the gateway verifies the epic before creating anything.

**How:**
- Premise: the M5 path is ready and the mock is reset.
- Exercise: call `create_story` for `IAM` with `epic_key: IAM-101`; read the mock's request log.
- Outcome: the response is `ok` with `epic_key: IAM-101`, and the mock saw the lookup of `IAM-101` before the create request.

**Evidence:** `mcp_response.json`, `create.json`, `mock_requests.json`

### M5-T10 — “Invalid same-project epic denies”

**What it tests:** Pointing at an IAM issue that is not an epic stops the request before any story is created.

**How:**
- Premise: the M5 path is ready and the mock is reset.
- Exercise: call `create_story` for `IAM` with `epic_key: IAM-900` (exists, but is not an Epic).
- Outcome: Codex receives `ok: false` with reason `epic_invalid`, and the mock received no create (`POST /rest/api/3/issue`).

**Evidence:** `mcp_response.json`, `error.json`, `mock_requests.json`

### M5-T11 — “NAS project story creation denies at capiss”

**What it tests:** Creating in an unauthorized project is refused at the mint.

**How:**
- Premise: the M5 path is ready and the mock is reset.
- Exercise: call `create_story` for `NAS`.
- Outcome: Codex receives `ok: false` with reason `mint_denied`, and the mock received no requests.

**Evidence:** `mcp_response.json`, `error.json`, `mock_requests.json`

### M5-T12 — “IAM token with NAS payload denies”

**What it tests:** A valid IAM create token cannot be spent on a different project by changing the request body.

**How:**
- Premise: an IAM `create_story` token is minted.
- Exercise: direct gateway call to `/mcp/jira/stories` with that token and `project_key: NAS`.
- Outcome: HTTP 403 with reason `project_mismatch`, and the mock received no requests.

**Evidence:** `create_mint.json`, `response.json`, `status.txt`, `mock_requests.json`

### M5-T13 — “IAM token with NAS epic denies”

**What it tests:** A story in IAM cannot be attached to an epic in another project, and the cross-project epic is not even looked up.

**How:**
- Premise: the M5 path is ready and the mock is reset.
- Exercise: call `create_story` for `IAM` with `epic_key: NAS-101`.
- Outcome: reason `epic_invalid`, and the mock received no requests at all.

**Evidence:** `mcp_response.json`, `error.json`, `mock_requests.json`

### M5-T14 — “Arbitrary create fields are rejected”

**What it tests:** Only the approved story fields are accepted; extra Jira fields cannot be smuggled in.

**How:**
- Premise: an IAM `create_story` token is minted.
- Exercise: direct gateway call with an extra `assignee` field.
- Outcome: HTTP 400 with reason `payload_invalid`, and no upstream request.

**Evidence:** `response.json`, `status.txt`, `mock_requests.json`

### M5-T15 — “Plain text only and raw ADF rejected”

**What it tests:** Descriptions must be plain text; a caller cannot pass raw Atlassian Document Format.

**How:**
- Premise: an IAM `create_story` token is minted.
- Exercise: direct gateway call with `description` as an ADF object (`{"type": "doc"}`).
- Outcome: HTTP 400 with reason `payload_invalid`, and no upstream request.

**Evidence:** `response.json`, `status.txt`, `mock_requests.json`

### M5-T16 — “Adapter forwards NAS to capiss”

**What it tests:** The adapter is not a policy engine: it forwards the NAS request to capiss and reports capiss's refusal, rather than deciding locally.

**How:**
- Premise: the M5 path is ready and the mock is reset.
- Exercise: call `read_project_summary` for `NAS`.
- Outcome: Codex receives reason `mint_denied`; the adapter's stderr records `mint_denied` and never `local_authorization`; the mock received no requests.

**Evidence:** `mcp_response.json`, `error.json`, `adapter.err`, `mock_requests.json`

### M5-T17 — “Unsupported action cannot be minted”

**What it tests:** Actions outside the approved pair cannot be minted, even for the allowed project.

**How:**
- Premise: capiss material is ready.
- Exercise: mint `act=update_story` on `jira-mcp:/project:IAM` with the adapter identity.
- Outcome: HTTP 403 with reason `policy`.

**Evidence:** `mint.json`, `status.txt`

### M5-T18 — “Old Jira tool authority is separate”

**What it tests:** The adapter cannot borrow the M4 `jira-tool` authority family.

**How:**
- Premise: capiss and the M5 path are ready.
- Exercise: as the adapter, mint `aud=jira-tool`, `act=read`, `res=jira-tool:/project:IAM`.
- Outcome: HTTP 403 with reason `policy`.

**Evidence:** `mint.json`, `status.txt`

### M5-T19 — “M5 does not disturb existing jira-tool path”

**What it tests:** Adding M5 left the M4 Jira path in place.

**How:**
- Premise: the OPA policy still contains the `jira-tool` audience and `jira-tool:/project:IAM` rules.
- Exercise: check that capiss material is present and `jira-tool-envoy` resolves and accepts TCP connections on port 10443.
- Outcome: the `jira-tool-envoy` address was resolved.
- Note: this is a presence check of the M4 path. Despite the guard's wording ("identity verified"), no SPIFFE identity is checked here; the M4a/M4b suites prove that path's behavior.

**Evidence:** guard outputs only

### M5-T20 — “Endpoint-bound action is enforced”

**What it tests:** A token is valid only for the endpoint matching its action.

**How:**
- Premise: an IAM `read_project_summary` token and an IAM `create_story` token are minted.
- Exercise: use the read token on `/mcp/jira/stories`, and the create token on `/mcp/jira/project-summary`.
- Outcome: both are denied with reason `act_mismatch`.

**Evidence:** `read_on_create.json`, `create_on_read.json` and their status files

### M5-T21 — “Audience mismatch denies”

**What it tests:** An M5 resource cannot be minted under a different audience.

**How:**
- Premise: capiss material is ready.
- Exercise: mint `aud=jira-tool` with `act=read_project_summary` on `jira-mcp:/project:IAM`.
- Outcome: the mint is refused with HTTP 400 or 403 (either is accepted; the test does not pin the reason).

**Evidence:** `mint.json`, `status.txt`

### M5-T22 — “Stolen token subject mismatch denies”

**What it tests:** A token stolen from the adapter is useless to another workload.

**How:**
- Premise: an IAM read token is minted for the adapter.
- Exercise: the rogue identity presents that token to the gateway's summary endpoint over its own mTLS connection.
- Outcome: HTTP 403 with reason `subject_mismatch`.

**Evidence:** `read_mint.json`, `response.json`, `status.txt`

### M5-T23 — “Invalid token denies”

**What it tests:** A malformed token is rejected before any upstream use.

**How:**
- Premise: the gateway is ready and the mock is reset.
- Exercise: direct gateway call with the token `not-a-token`.
- Outcome: HTTP 401 with reason `token_invalid`, and no upstream request.

**Evidence:** `response.json`, `status.txt`, `mock_requests.json`

### M5-T24 — “Direct app bypass is unavailable”

**What it tests:** The gateway application cannot be reached without going through its Envoy boundary.

**How:**
- Premise: the M5 edge path is reachable.
- Exercise: from the test harness, request `http://jira-mcp-gateway:8080/health` directly.
- Outcome: the request fails with a name-resolution, timeout, no-route, or connection failure.

**Evidence:** `direct_gateway.out`, `direct_gateway_rc.txt`

### M5-T25 — “Only gateway calls mock upstream”

**What it tests:** Every upstream request originates from the gateway.

**How:**
- Premise: the M5 path is ready and the mock is reset.
- Exercise: make an allowed IAM summary call and a denied NAS summary call.
- Outcome: the mock received at least one request, and every request carries the `jira-mcp-gateway` marker.

**Evidence:** `iam.json`, `nas.json`, `mock_requests.json`

### M5-T26 — “MCP responses contain no capiss tokens”

**What it tests:** Codex never sees capability tokens or credentials.

**How:**
- Premise: the M5 path is ready.
- Exercise: call `read_project_summary` and `create_story` through MCP.
- Outcome: neither response contains `Bearer `, `token_type`, a `"token"` field, `Biscuit`, or `JIRA_API_TOKEN`.

**Evidence:** `summary_mcp.json`, `create_mcp.json`

### M5-T27 — “Adapter logs contain no bearer tokens”

**What it tests:** The adapter's diagnostics carry decision metadata but no token material.

**How:**
- Premise: the M5 path is ready.
- Exercise: call `read_project_summary` and keep the adapter's stderr.
- Outcome: stderr contains an `adapter_decision` event and no `Bearer `, `"token"`, `token_type`, or `Biscuit`.

**Evidence:** `summary_mcp.json`, `adapter.err`

### M5-T28 — “Adapter environment has no Jira API key”

**What it tests:** The Jira credential lives only in the gateway, never in the component Codex talks to.

**How:**
- Premise: the adapter container is running.
- Exercise: capture the adapter container's environment.
- Outcome: none of `JIRA_API_TOKEN`, `JIRA_EMAIL`, or `JIRA_BASE_URL` is set.

**Evidence:** `adapter_env.txt`

### M5-T30 — “Client auth headers are stripped upstream”

**What it tests:** The caller's capability token is not forwarded to Jira.

**How:**
- Premise: the M5 path is ready and the mock is reset.
- Exercise: create a story through MCP.
- Outcome: in mock mode, every request the mock received has no `Authorization` header.

**Evidence:** `create_mcp.json`, `mock_requests.json`

### M5-T31 — “Summary participates in budget governance”

**What it tests:** Read tokens have a use budget.

**How:**
- Premise: one IAM read token is minted.
- Exercise: call the summary endpoint 11 times with the same token.
- Outcome: exactly 10 calls return 200; the 11th returns 403 with reason `budget_exhausted`.

**Evidence:** `statuses.txt`, `resp_1.json` … `resp_11.json`

### M5-T32 — “Create consumes budget before upstream”

**What it tests:** A successful create is recorded with its remaining budget by the gateway.

**How:**
- Premise: the M5 path is ready; a log start time is recorded.
- Exercise: create a story through MCP; capture gateway logs since the start time.
- Outcome: the gateway logged an `allow` decision for `story_create` with a numeric `budget_remaining`.

**Evidence:** `create_mcp.json`, `gateway.log`

### M5-T33 — “Budget exhaustion denies create”

**What it tests:** Create tokens stop working once their budget is spent.

**How:**
- Premise: one IAM create token is minted.
- Exercise: create 10 stories with it, then try an 11th.
- Outcome: the 11th returns 403 with reason `budget_exhausted`.

**Evidence:** `create_1.json` … `create_10.json`, `denied.json`, `denied_status.txt`

### M5-T34 — “Pre-validation denials do not consume budget”

**What it tests:** A request rejected for its payload does not block a following valid request.

**How:**
- Premise: one IAM create token is minted.
- Exercise: send an invalid create (ADF description), then a valid create with the same token.
- Outcome: the invalid one returns 400 and the valid one returns 201.
- Note: with a budget of 10 this shows the rejection did not exhaust the token; it does not on its own prove the counter was left unchanged.

**Evidence:** `invalid.json`, `valid.json` and their status files

### M5-T35 — “Upstream create failure is not refunded”

**What it tests:** An upstream failure after authorization is reported in a standard form.

**How:**
- Premise: one IAM create token is minted and the mock is armed to fail the next create.
- Exercise: send an authorized create.
- Outcome: HTTP 502 with reason `upstream_error`.
- Note: the test does not read the budget afterwards, so "not refunded" is not directly asserted here.

**Evidence:** `fail.json`, `fail_status.txt`

### M5-T36 — “Read audit events correlate”

**What it tests:** An allowed summary leaves both a mint event and a gateway event.

**How:**
- Premise: the M5 path is ready; a log start time is recorded.
- Exercise: call `read_project_summary` for `IAM`; capture capiss and gateway logs since the start time.
- Outcome: the gateway logged an `allow` for `project_summary` with `aud=jira-mcp-gateway` and `act=read_project_summary`, and capiss logged an `allow` mint for the same audience and action.
- Note: the two events are checked for presence and matching audience/action; joining by correlation id is proven by the trace tests (M5-T49 onward).

**Evidence:** `summary.json`, `capiss.log`, `gateway.log`

### M5-T37 — “Create audit events correlate”

**What it tests:** An allowed create leaves a gateway event naming the created issue.

**How:**
- Premise: the M5 path is ready; a log start time is recorded.
- Exercise: create a story; capture gateway logs.
- Outcome: the gateway logged an `allow` for `story_create` that includes the new `issue_key`.

**Evidence:** `create.json`, `gateway.log`

### M5-T38 — “Deny paths produce final decision evidence”

**What it tests:** Denials are logged as decisions, not silently dropped.

**How:**
- Premise: an IAM create token is minted; a log start time is recorded.
- Exercise: send a create with an ADF description; capture gateway logs.
- Outcome: the gateway logged a `deny` decision with reason `payload_invalid`.

**Evidence:** `response.json`, `status.txt`, `gateway.log`

### M5-T39 — “Local errors avoid upstream existence leak”

**What it tests:** A refused request reveals nothing about what exists upstream.

**How:**
- Premise: the mock's breadth report shows that project `NAS` exists.
- Exercise: call `read_project_summary` for `NAS`.
- Outcome: the error is `mint_denied` and carries no `project` or `issues` data.

**Evidence:** `breadth.json`, `error.json`

### M5-T40 — “Mock upstream breadth precondition”

**What it tests:** The mock is genuinely broader than the agent's authority, so the narrowing tests mean something.

**How:**
- Premise: `jira-mcp-mock` resolves.
- Exercise: read the mock's breadth report.
- Outcome: projects are exactly `IAM` and `NAS`, with more than 75 IAM issues and at least 4 NAS issues.

**Evidence:** `breadth.json`

### M5-T41 — “Protected path narrows broad mock”

**What it tests:** Through the protected path, that broad upstream narrows to IAM only.

**How:**
- Premise: the breadth report is captured and the M5 path is ready.
- Exercise: call `read_project_summary` for `IAM` and for `NAS`.
- Outcome: IAM returns `ok` for project `IAM`; NAS returns `mint_denied`.

**Evidence:** `breadth.json`, `iam.json`, `nas.json`

### M5-T42 — “Varambu capiss audit files”

**What it tests:** The Varambu audit tailer writes every capiss mint decision for the session to a JSONL file and a readable log, with enriched fields and no secrets.

**How:**
- Premise: the M5 path is ready; a fresh audit session is created and marked current.
- Exercise: start the capiss audit tailer; make four MCP calls (IAM read, IAM create, NAS read, NAS create); wait for four entries; render `varambu audit --json`.
- Outcome:
  - the file holds the decisions in request order: allow read, allow create, deny NAS, deny NAS;
  - allowed rows carry the adapter subject, token and root-token ids, issued/expiry times in UTC and local time, TTL, and correlation id;
  - denied rows carry reason `policy`, the NAS project, and no token-validity fields;
  - no bearer token, `Basic` credential, or `JIRA_API_TOKEN` appears in the files or the CLI output;
  - the human log shows `MINTED OK`, `DENIED: Reason Policy`, and `Logged At:`.

**Evidence:** `capiss_audit.jsonl`, `capiss_audit.log`, `varambu_audit_json.out`, and the four MCP responses

### M5-T43 — “Varambu audit active append without post-processing”

**What it tests:** Audit entries are appended live as decisions happen, and the CLI shows exactly what was persisted.

**How:**
- Premise: an empty audit session is prepared.
- Exercise: start the tailer; make one allowed call and snapshot the file; render `varambu audit --json`; make one denied call and snapshot again.
- Outcome: the first snapshot has exactly one entry; the CLI output is byte-identical to that persisted entry; the second snapshot has two entries, allow then deny.

**Evidence:** `after_first.jsonl`, `varambu_after_first.out`, `after_second.jsonl`

### M5-T44 — “Varambu audit current session history and file access”

**What it tests:** `varambu audit` shows the current session by default, every session with `--all`, and points to the real files.

**How:**
- Premise: two synthetic sessions exist — session 1 with an allowed record, session 2 with a denied record — and `current` points to session 2.
- Exercise: run `varambu audit`, `varambu audit --all`, `varambu audit-file`, and `varambu audit-file --all`.
- Outcome: the default view shows only the denied record; `--all` shows both records exactly once each (no merging); the reported file paths exist; `audit-file --all` lists both sessions' files.

**Evidence:** `current.out`, `all.out`, `paths.out`, `paths_all.out`

### M5-T45 — “Varambu audit secret exclusion in persisted evidence”

**What it tests:** No credential material reaches any persisted audit artifact.

**How:**
- Premise: an audit session is prepared.
- Exercise: start the tailer; make two allowed calls and one denied call; render the CLI output.
- Outcome: no bearer token values in the JSONL; no `Bearer`/`Basic` in the human log or CLI output; no credentials in the tailer's diagnostics; token ids contain only hexadecimal characters and dashes.

**Evidence:** `capiss_audit.jsonl`, `capiss_audit.log`, `audit_tailer.err`, `varambu_audit.out`

### M5-T46 — “Varambu audit stale tailer warning and strict failure”

**What it tests:** If the audit tailer has died, the operator is told — and strict mode fails.

**How:**
- Premise: a session with one record and a tailer PID that is not running.
- Exercise: run `varambu audit`, then `varambu audit --strict`.
- Outcome: the normal run prints a tailer warning on stderr and still shows the persisted record; the strict run exits non-zero.

**Evidence:** `audit_warn.out`, `audit_warn.err`, `strict_rc.txt`

### M5-T47 — “Varambu audit local and UTC timing semantics”

**What it tests:** Audit times are unambiguous: UTC plus local time with its zone.

**How:**
- Premise: an audit session is prepared.
- Exercise: start the tailer; make one allowed and one denied call.
- Outcome:
  - the allowed record has a UTC timestamp ending in `Z`, a local timestamp with a zone name, and a timezone field;
  - it also has issued and expiry times in UTC and a positive TTL;
  - the denied record has logged timestamps but no issued, expiry, or TTL fields;
  - human log headers show a local date and time.

**Evidence:** `capiss_audit.jsonl`, the session's `capiss_audit.log`

### M5-T48 — “Varambu audit uniform capiss enrichment”

**What it tests:** Every audit record has the same enriched shape regardless of outcome.

**How:**
- Premise: an audit session is prepared.
- Exercise: start the tailer; make an IAM read, an IAM create, and a NAS read.
- Outcome:
  - every record has result, reason, UTC and local timestamps, timezone, policy id, and policy hash;
  - allowed records add token validity fields, and denied records never do;
  - no `Bearer` or `Basic` values appear.

**Evidence:** `capiss_audit.jsonl`

### M5-T49 — “Varambu trace full chain allowed”

**What it tests:** For one allowed request, `varambu trace` shows all seven legs in order, joined by the request's correlation id.

**How:**
- Premise: the M5 path and mock are ready; a trace session is prepared and marked current.
- Exercise:
  - start the capiss and gateway tailers and make an allowed `create_story` call that writes the adapter's own audit legs;
  - read the correlation id from the response;
  - write a Codex session record (rollout) containing the user's exact prompt, the tool call, and its result;
  - render the trace as JSON, and as text for this correlation id only.
- Outcome:
  - exactly one chain exists for the correlation id;
  - its legs are, in order, `intent`, `action`, `adapter_request`, `mint`, `gateway`, `upstream`, `adapter_decision`, all present;
  - the gateway leg is `allow` and the upstream leg shows status 201;
  - the intent leg holds the prompt verbatim;
  - the mint, gateway, and upstream legs carry the same correlation id;
  - the text view shows the adapter, mint, and "return to Codex" rows and the prompt.

**Evidence:** `trace.json`, `trace.txt`, `trace.jsonl`, `cid.txt`, `capiss_audit.jsonl`, `gateway_audit.jsonl`, `adapter_audit.jsonl`

### M5-T50 — “Varambu trace denied mint partial chain”

**What it tests:** A request refused at the mint shows an honest partial chain that ends at the denial.

**How:**
- Premise: a trace session is prepared.
- Exercise: start the tailers; make a denied NAS `read_project_summary` call; write a rollout whose result is `ok: false`; render the trace (text view for this correlation id only).
- Outcome:
  - the trace renders without errors;
  - the mint leg is present and `deny`;
  - the gateway and upstream legs are absent;
  - the adapter request leg is present;
  - the text view marks missing legs as "not yet available" rather than as errors.

**Evidence:** `trace.json`, `trace.txt`, `trace.err`, `capiss_audit.jsonl`, `adapter_audit.jsonl`

### M5-T51 — “Varambu trace intent pending then converges”

**What it tests:** If the agent's session record arrives late, the trace first shows the intent as pending and then fills it in.

**How:**
- Premise: a trace session is prepared.
- Exercise: make an allowed `create_story` call and capture the in-boundary legs; render the trace before any rollout exists; then write the rollout and render again.
- Outcome: the first render has no intent but does have the adapter request; the second render's intent for this correlation id holds the prompt verbatim.

**Evidence:** `trace_before.json`, `trace_after.json`, `cid.txt`

### M5-T52 — “Varambu trace multi tool-call attribution”

**What it tests:** One user turn that triggers two tool calls produces two chains, each attributed to the same prompt.

**How:**
- Premise: a trace session is prepared.
- Exercise: make an IAM read and an IAM create; write one rollout turn with the prompt followed by both calls and their results; render the trace.
- Outcome: two distinct chains exist, one per correlation id; both carry the same verbatim prompt; the read chain's action is `read_project_summary` and the create chain's is `create_story`.

**Evidence:** `trace.json`, `trace.jsonl`, `cid_a.txt`, `cid_b.txt`

### M5-T53 — “Varambu trace secret hygiene and bounds”

**What it tests:** Agent-supplied content is scrubbed and bounded before it is persisted in trace evidence.

**How:**
- Premise: a trace session is prepared.
- Exercise:
  - make an allowed create;
  - write a hostile rollout: a 3,000-character prompt, a 1,500-character summary, tool arguments carrying a fake `token` and `Authorization: Bearer` value, a reasoning block, and shell-command output;
  - render the trace.
- Outcome:
  - no bearer, basic, biscuit, cookie, or Jira secret values appear in the trace files or any audit source;
  - `token` and `authorization` arguments are dropped;
  - the prompt is truncated with a marker to at most about 2 KB, and the summary is truncated with a marker;
  - no reasoning or shell-command content is persisted.

**Evidence:** `trace.jsonl`, `trace.txt`, and the session's audit files

### M5-T54 — “Varambu trace agent tamper detection”

**What it tests:** An agent cannot rewrite history: if its session record claims success for a denied request, the in-boundary legs still show the truth.

**How:**
- Premise: a trace session is prepared.
- Exercise: make a denied NAS read; write a forged rollout claiming `ok: true` for that correlation id; render the trace (text view for this correlation id only).
- Outcome: the forged success is present in the rollout, but the mint leg is `deny`, the adapter's decision is `ok: false`, and the text view shows the denial.

**Evidence:** `trace.json`, `trace.txt`, the session's rollout file

### M5-T55 — “Varambu trace honest live upstream leg”

**What it tests:** Against real Jira, the upstream leg is labelled as attested by the gateway and nothing pretends to be an independent upstream record.

**How:**
- Premise: reads the gateway's `JIRA_MCP_UPSTREAM_MODE` and records it (`upstream_mode.txt`); if the gateway cannot be inspected the test fails.
- If the mode is not `live` (the default): the test writes `skip_reason.txt` (`env_gate=live_jira`), records a warning, and stops. `make qa-evidence` counts it as skipped, never as validated.
- If the mode is `live`: make an allowed create against real Jira, write a rollout, and render the trace in live mode.
- Outcome (live only): the upstream leg reads "gateway-attested, live", and no fabricated upstream event names appear.

**Evidence:** `upstream_mode.txt`, and `skip_reason.txt` plus a warning in default runs; `trace.txt` in live runs

### M5-T56 — “Varambu trace CLI surface and audit non-regression”

**What it tests:** The `varambu trace` options behave as documented, and adding trace did not change `varambu audit`.

**How:**
- Premise: two isolated synthetic trace sessions with fixed correlation ids; `current` points to the second.
- Exercise: run `varambu trace`, `trace --cid <id>`, `trace --all`, and `trace --json`; then `varambu audit`, `audit --all`, `audit --json`, and `audit-file`.
- Outcome:
  - the default view shows only the current session's chain;
  - `--cid` selects exactly that chain, `--all` shows both sessions, and `--json` is machine-readable;
  - `audit` still shows only the current session's record, `audit --json` parses, and `audit-file` resolves the capiss file paths.

**Evidence:** `trace_default.out`, `trace_cid.out`, `trace_all.out`, `trace_json.out`, `audit.out`, `audit_all.out`, `audit_json.out`, `audit_file.out`

### M5-T57 — “Varambu trace canonical ordering and join integrity”

**What it tests:** With several requests in one session, every chain keeps its legs in the fixed order and never borrows another chain's legs.

**How:**
- Premise: a trace session is prepared.
- Exercise: make two allowed creates; write two rollout turns; render the trace.
- Outcome: every chain lists its legs in canonical order; legs are joined only by correlation id with no leakage between chains; two chains with distinct ids exist; every present leg keeps its own UTC timestamp and sequence number.

**Evidence:** `trace.json`, `cid_a.txt`, `cid_b.txt`

### M5-T58 — “Varambu trace anchor rule mint reuse and timestamps”

**What it tests:** Only requests that entered through the adapter become chains, and the mint leg reuses capiss's own record.

**How:**
- Premise: a trace session is prepared.
- Exercise:
  - make an allowed create and write its rollout;
  - after the tailers stop, add a capiss-only mint record for an unrelated non-M5 request (`agent-a` reading `tool-b`);
  - render the trace in the `Europe/Berlin` timezone, as text for this correlation id only.
- Outcome:
  - the M5 request appears as exactly one chain, and the unrelated mint does not appear;
  - the text view shows this request's own token id (taken from the capiss record with this correlation id) and its `create_story` grant;
  - every present leg carries UTC time, local time, and a sequence number.

**Evidence:** `trace.json`, `trace.txt`, `cid.txt`

### M5-T59 — “Varambu trace separates gateway allow from upstream deny”

**What it tests:** When Jira itself rejects a call the gateway allowed, the trace makes clear who said no.

**How:**
- Premise: a synthetic session in which the gateway allowed a request and the upstream returned 401.
- Exercise: render the trace as JSON and text in live mode.
- Outcome:
  - the gateway leg is `allow`, and the upstream leg is `fail` with status 401;
  - the text view shows the gateway row as ALLOW and the upstream row as 401 FAIL;
  - the upstream leg is labelled "gateway-attested, live";
  - Jira's error detail ("Unauthorized — the Jira credential was rejected") is shown verbatim, with no added interpretation.

**Evidence:** `trace.json`, `trace.txt`
