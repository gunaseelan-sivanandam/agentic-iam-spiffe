# Retirement Contract

## Logic to remove
- Dead code: none exists for Jira before this slice.
- Duplicated logic superseded by shared code: none; shared PEP extraction is deferred deliberately.
- Compatibility shortcuts to retire: none in M4a. `/capabilities/mint` remains for existing compatibility and gets an OPL follow-up only.

## Artifact cleanup
- Remove or avoid unused Jira compose profiles, demo helpers, or mock endpoints not used by tests/demo.
- Do not leave generated live-smoke evidence in tracked files.
- Do not add Confluence placeholder artifacts.

## Deferred retention
- OPL follow-up: retire `/capabilities/mint` compatibility endpoint after existing M3/M4 tests and docs move to `/capabilities/root-mint`.
- OPL follow-up: replace static policy version strings with a real computed policy hash for capiss mint-decision audit events.
