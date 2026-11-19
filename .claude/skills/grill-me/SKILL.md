---
name: grill-me
description: Interview the user about a plan or design until reaching a shared understanding, resolving each branch of the design one decision at a time. Use when a slice's design or approach is not clear.
---

# Grill-me — the discovery interview of a slice

This skill runs the interview of the discovery stage (`AGENTS.md`, slice workflow, discovery) when a slice's design
or approach is not clear, so that every open choice becomes a decision the plan records with its source. It is a
prompt, versioned and reviewed in this repository like any other.

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each
branch of the design, resolving the decisions it depends on one by one.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

Always ask which keys, sockets and secrets the slice touches and who may hold them, against the holders in
`security/invariants.yaml`.
