# Test Specification (Detailed)

Each test below is derived directly from `docs/test_spec.md`. Text is a plain-English rendering of the guard intent and evidence capture already present in the harness. If a detail is not explicit in the harness, it is marked as UNKNOWN.

## Milestone 1 - Server and agent connection and successful entry

### T1 — “Rogue missing join token rejects attestation”
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

### T2 — “Rogue forged join token rejects attestation”
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

### T3 — “Rogue replayed join token rejects attestation”
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

### T4 — “Rogue repeated attestation attempt is rejected”
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

### T5 — “Rogue without Workload API socket cannot fetch SVID”
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

### T1 — “Rogue without SVID cannot access /secret”
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

### T2 — “Rogue with invalid client cert is rejected”
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

### T3 — “Rogue with expired client cert is rejected”
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

### T4 — “Rogue with wrong SPIFFE ID is rejected”
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

### T5 — “Rogue without Workload API socket cannot fetch SVID”
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

### T6 — “Rogue with socket but no entry cannot fetch SVID”
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

### T7 — “Rogue cannot read SVIDs or keys”
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

### T8 — “No unintended SPIRE entries created”
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

### T9 — “Rogue with expired short-lived SVID is rejected”
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

### T1 — “tool-b app not reachable from edge network”
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

### T2 — “tool-b rejects missing x-spiffe-id header”
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

### T3 — “tool-b rejects mismatched x-spiffe-id header”
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

### T1 — “agent-a can mint (allowed by OPA)”
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

### T2 — “rogue mint denied by policy”
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

### T3 — “OPA is not reachable from edge”
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

### T4 — “Fail closed when OPA is unavailable”
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

### T5 — “Issuer app not reachable from edge”
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

### T1 — “mint returns non-empty token”
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

### T2 — “expires_at is present and in the near future”
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

### T3 — “two mints produce different tokens”
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

### T1 — “identity-only access to /secret is denied”
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

### T2 — “agent-a can access /secret with minted capability”
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

### T3 — “rogue cannot access /secret without token”
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

### T4 — “stolen token replay by rogue is rejected (sub mismatch)”
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

### T5 — “expired token is rejected”
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

### T6 — “mint rejects missing parameters”
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

### T7 — “mint denies unapproved authority request”
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

### T1 — “root mint includes chain metadata”
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

### T2 — “search writes discovery registry entries”
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

### T3 — “resource mint requires registry proof”
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

### T4 — “resource mint after discovery allows read-file”
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

### T5 — “budget is enforced per root token”
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

### T6 — “tampered token is denied”
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

### T7 — “depth limit is enforced on repeated delegation”
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

### T8 — “new-resource mint rate is enforced at capiss”
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

### T9 — “allow flow emits correlatable audit events”
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

### T10 — “deny flow emits correlatable mint audit event”
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

### T11 — “amplified delegated mint is denied”
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

### T12 — “wildcard delegated resource is denied”
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

### T13 — “budget and registry TTLs are bounded by root expiry”
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

### T14 — “protected request does not require capiss hot path”
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

### M4a-T1 - mock upstream breadth
Directly reads `IAM-1` and `NAS-1` from `jira-mock` to prove the upstream test data is broader than the agent's allowed project.

### M4a-T2 - allowed mint and IAM read
Mints `aud=jira-tool`, `act=read`, `res=jira-tool:/project:IAM` for agent-a, reads `IAM-1` through `jira-tool-envoy`, and records the verified `jira-tool-envoy` SPIFFE identity.

### M4a-T3 - non-allowed project mint denied
Attempts a NAS Jira root mint as agent-a and expects `403` with reason `policy`.

### M4a-T4 - NAS read denied before upstream
Uses an IAM read token against `NAS-1`, expects `403` with reason `project_mismatch`, and verifies the mock request log is empty.

### M4a-T5 - rogue Jira mint denied
Attempts an IAM Jira root mint using rogue client material and expects `403` with reason `policy`.

### M4a-T6 - stolen Jira token denied
Mints an IAM token as agent-a, reuses it with rogue client material, and expects `403` with reason `sub_mismatch` before upstream use.

### M4a-T7 - Jira budget consumption
Reads `IAM-1` once with an IAM token and verifies Redis budget remaining is `9`.

### M4a-T8 - Jira budget exhaustion
Performs eleven protected reads with one IAM token, expects the first ten to succeed and the eleventh to deny with `budget_exceeded`, and verifies only ten upstream calls occurred.

### M4a-T9 - upstream project mismatch denied
Reads the mismatch fixture `IAM-999`, expects `upstream_project_mismatch`, and verifies the mismatched upstream body is not returned.

### M4a-T10 - Jira audit trace reconstruction
Captures capiss and jira-tool logs after an allowed read and verifies correlated `capiss_mint_decision` and `jiratool_enforcement_decision` events.

## Milestone 4b - Jira project-scoped description write

These tests are implemented in `scripts/rogue_node_tests.sh` as `M4B_T1_test` through `M4B_T6_test`. They prove `act=write` is project-scoped read plus description replacement only. `act=read` cannot write, malformed or overbroad bodies are rejected locally, and NAS writes are denied before any upstream call.

### M4b-T1 - allowed write update and readback
Mints `aud=jira-tool`, `act=write`, `res=jira-tool:/project:IAM`, writes a timestamp marker to `IAM-1`, reads the issue back with the write token, and verifies the mock saw PUT then GET.

### M4b-T2 - read token write denied
Mints an IAM read token, attempts description PUT, and expects `403` with reason `insufficient_authority` and no mock write.

### M4b-T3 - NAS write mint denied
Attempts a NAS write root mint as agent-a and expects `403` with reason `policy`.

### M4b-T4 - NAS write denied before upstream
Uses an IAM write token against `NAS-1`, expects `403` with reason `project_mismatch`, and verifies no mock request occurred.

### M4b-T5 - description write body shape
Sends malformed JSON and a body containing both `description` and `summary`, expects `400` with `malformed_body` or `unsupported_fields`, and verifies no mock request occurred.

### M4b-T6 - write audit trace reconstruction
Mints an IAM write token, writes and reads `IAM-2`, captures capiss and jira-tool logs, and verifies correlated write mint plus jira-tool write/read allow events.
