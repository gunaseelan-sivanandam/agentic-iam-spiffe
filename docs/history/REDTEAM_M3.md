# Red Team Report — Milestone 3

## Executive Summary

Status: **NO FINDINGS**  
I executed the red-team script against a running stack and did not observe any
capability bypasses or network boundary violations. All planned attack cases
ran to completion.

## Tested Attack Cases

Executed (from rogue container):

- A1–A3: Network boundary checks from rogue to OPA / capiss app / tool-b app
- B1–B5: Mint endpoint abuse (missing fields, type confusion, path/aud/act variants, high-rate)
- C1, C3: Token misuse against tool-b (identity-only, garbage token)
- D1–D2: Header spoof attempts

No partials; all cases executed.

## Findings

No security bypasses observed in the executed cases. Full coverage requires a
rerun with the updated script.

## Reproduction Steps (to run on a host with Docker access)

1) Start the stack:

```bash
docker compose -f compose/spiffe.compose.yml up -d \
  spire-server spire-token-init spire-agent \
  tool-b tool-b-envoy \
  capability-issuer capability-issuer-envoy \
  capability-issuer-no-opa capability-issuer-no-opa-envoy \
  opa agent-a rogue
```

2) Ensure `agent-a` and `rogue` are running (long-lived for `docker exec`):

```bash
docker rm -f spiffe-agent-a spiffe-rogue 2>/dev/null || true
docker compose -f compose/spiffe.compose.yml run -d --name spiffe-agent-a --entrypoint sleep agent-a infinity
docker compose -f compose/spiffe.compose.yml run -d --name spiffe-rogue --entrypoint sleep rogue infinity
```

3) Run the red-team script:

```bash
sh scripts/redteam/run_m3_redteam.sh
```

4) Re-run the full test suite to confirm no regressions:

```bash
docker compose --profile tests -f compose/spiffe.compose.yml up --build --abort-on-container-exit rogue-tests
```

## Notes

- The red-team script relies on `docker exec` to drive black-box calls from the
  `rogue` and `agent-a` containers.
- If any attack succeeds (minting as rogue, reading `/secret` without valid
  capability, header spoofing, OPA access from edge), treat as a finding and
  record the exact command and response.

## Observed Results (first run)

- A1–A3: PASS (OPA/capiss/tool-b apps not reachable from rogue)
- B1: 400 bad_request for missing/invalid fields
- B3/B4/B2: 403 policy for aud/act/res mismatches
- B5: rogue minting denied across 20 attempts
- B6: 503 opa_unavailable when using no-OPA Envoy
- C1: 401 missing_token
- C3: 401 invalid_token
- C4: 403 sub_mismatch for stolen agent-a token replay
- C6: 401 invalid_token for tampered token
- C5: 403 expired when agent-a reuses the token after expiry
- D1/D2: 401 missing_token (spoofed header ineffective)

Issues in run: none.
