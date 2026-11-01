# Slice Plan — agent-identity

## Goal
- Agents act on GitHub as their own machine user, `gunaseelan-agent`, instead of the owner's
  account, so the history shows what an agent did, and the `main` ruleset can require the owner's
  approving review (GitHub issue #20).

## Grill-Me Review Summary
- Grill-me with the user on 2026-10-31 and 2026-11-01; the user asked to keep it short and approved
  plan and implementation in one PR, as for `backlog-issues` (2026-11-01: "yes", in reply to "Do you
  want this as one PR …").
- **D1 Machine user**, not a GitHub App or a different git author only. A GitHub App gives
  short-lived tokens, which defend against theft (outside the threat model), at the cost of a private
  key and a token-minting script; a git author alone leaves PRs, issues and pushes in the owner's name.
- **D2 Name:** `gunaseelan-agent`, account email `gunaseelansivanandam+agent@gmail.com`, commits as
  `gunaseelan-agent <351220647+gunaseelan-agent@users.noreply.github.com>` (the bot's no-reply
  address).
- **D3 One classic token for `gh` and `git`:** scopes `repo`, `read:org`, `workflow`, 90-day expiry;
  pushes over HTTPS through `gh` as git's credential helper. No separate SSH key.
- **D4 The identity belongs to the agent session, not to the repository clone:** the gitignored
  `.claude/settings.local.json` sets `GH_CONFIG_DIR` and `GIT_AUTHOR_*` / `GIT_COMMITTER_*`; the
  owner's own terminal stays the owner. `.git/config` keeps the owner's `user.name`; only `origin`
  changes to HTTPS.
- **D5 The `main` ruleset requires one approving review**, no bypass actors. The bot cannot approve
  its own PR; the owner approves and merges. `make gate-consistency` fails if the ruleset requires no
  approving review (it already reads the ruleset).
- **D6 `AGENTS.md` Git rules** say agents act as the bot, the owner approves and merges, how a
  session gets the identity, and that an agent checks `gh api user --jq .login` before a GitHub write.
- The two inactive write collaborators (environment facts) stay; their approval would count, but
  neither is an agent, so this is outside the delivery threat model. The owner may remove them.

## Threat model for review
- Delivery: agents make honest mistakes (AGENTS.md, PoC scope and proportion). The miss this slice
  prevents: an agent merges its own PR, or its work is indistinguishable from the owner's. A wrong
  ruleset edit (approval turned off) must fail a gate.
- System under test: not touched.

## Requirements
- None added or changed: this is delivery process, not system behaviour.

## Success criteria
- `gh api user` in an agent session prints `gunaseelan-agent`; commits from the session carry the
  bot's no-reply address; this PR is opened and pushed by the bot.
- The `main` ruleset has `required_approving_review_count: 1` and no bypass actors.
- `make gate-consistency` fails on a ruleset without a required approval and passes on the live one.

## In scope
- `scripts/check_gate_consistency.py` and its tooling tests; `AGENTS.md` (Git rules, gate-consistency
  row); closing DPL-008 and issue #18 (the user turned on "Automatically delete head branches");
  `docs/STATUS.md`, the slice index, the implementation log.

## Out of scope
- Refusing agent reads of the owner's `gh` config or SSH key (slice 3 hooks, #16).
- Listing host credentials in `security/invariants.yaml`: it registers the system under test's
  assets, not delivery credentials.
- Token rotation tooling: an expired token fails `gh` and `git push` loudly; the owner creates a new
  one.
- The Codex reviewer: it runs read-only with no network and never writes to GitHub.

## Assets and holders
- New: the bot's token, in `/home/guna/.config/gh-agent/hosts.yml` (mode `600`, owner `guna`),
  outside the repository. Holder: agent sessions on the owner's host (through `GH_CONFIG_DIR`). It
  never enters the repository, CI, the stack or evidence. Accepted PoC simplification: credentials
  live in files on one host.
- Unchanged: the owner's token (`~/.config/gh/hosts.yml`) and SSH key (`~/.ssh/id_ed25519`).
  Residual: agents run as the owner's OS user and could read them; under the honest-mistake model an
  agent does not use them on purpose, and the AGENTS.md identity check catches a session that falls
  back to the owner's login.
- No key, socket or secret of the system under test is touched.

## Environment facts
Probed 2026-10-31 and 2026-11-01, without printing token values:
- Repository: personal (owner type `User`), public; `delete_branch_on_merge: true` (set by the owner).
- Collaborators before the slice: `gunaseelan-sivanandam` (admin), `dreiundzwanzig23` (write),
  `hariprasath-sivanandam` (write); the owner says no one else works on the repository.
- GitHub token documentation (2026-11-01): fine-grained tokens cannot be used "to contribute to
  repositories where the user is an outside or repository collaborator", so the bot needs a classic
  token. `gh` 2.4.0 needs at least `repo` and `read:org` (`gh auth login --help`).
- `~/.gitconfig` sets `credential.https://github.com.helper` to `!/usr/bin/gh auth git-credential`,
  so with `GH_CONFIG_DIR` set, HTTPS pushes use the bot's token (D4).
- Bot login (2026-11-01): `gh api user` → `gunaseelan-agent`, id 351220647, 2FA on; repository
  permission push, not admin; token expiry 2027-01-30. The token has extra scopes (`audit_log`,
  `read:project`, `read:user`, `user:email`, `write:discussion`); unneeded but harmless (the bot owns
  nothing and reaches only this repository); drop them at renewal.
- Ruleset `basic` (26054924) after the owner's change: `pull_request` with
  `required_approving_review_count: 1`; the public API without a token shows it, which is what
  `make gate-consistency` reads.

## Hidden-state and trust decisions
- No runtime state. The session's identity lives in `.claude/settings.local.json` (gitignored; writer:
  the owner; reader: Claude Code at session start); authoritative for which GitHub account an agent
  uses.

## Authored source changes
- Requirements: none. Architecture: none. Runtime proof: none.
- Rulebook: `AGENTS.md` Git rules (D6) and the gate-consistency threshold (D5).
- QA tooling: `scripts/check_gate_consistency.py` checks the required approval.

## Retirement and compatibility
- The Git rule "GitHub does not enforce this yet …" is removed. `origin` over SSH is replaced by
  HTTPS in this clone (local configuration, not in the repository). Nothing else is retired.

## Review notes
- The owner's own PRs would need another account's approval (no bypass actors); the owner opens no
  PRs today. If that changes, adding the admin role to the bypass list is the owner's choice.
