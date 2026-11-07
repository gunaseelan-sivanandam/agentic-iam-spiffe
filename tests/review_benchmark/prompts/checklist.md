# Review task (full checklist)

Review the change for defects that matter within the threat model of the approved rules. Work
through every question below and answer each one; "none" needs a reason.

1. **Intent.** Does it do what was asked or approved, no more and no less?
2. **Claims and evidence.** For each claim (test, doc, PR text, requirement), what proves it? Could
   the proof hold while the claim is false? Is each requirement verifiable and unambiguous?
3. **Design and quality.** Simplest design that fits, consistent with its surroundings, readable and
   maintainable; real alternatives considered; each relevant quality (reliability, performance,
   operability and diagnosability, usability of docs or CLI, compatibility) no worse than before.
4. **Failure and change.** Behaviour on invalid input, dependency failure, partial failure, timing or
   concurrency; fails safe; can be rolled back or migrated.
5. **Rules and new risks.** Keeps every standing rule and invariant (the rulebook, requirements,
   asset holders, open problems); registers and threat-checks any new asset, trust boundary, data
   flow, dependency or rule it adds.
6. **Ripple.** What depends on what changed, and is each dependent still correct or updated?
7. **Durability.** Does anything decided or learned live only somewhere temporary? Where must it
   live?
8. **Blind spots.** What was not checked, and could it matter?

Report each defect as a finding with its exact location (file and line in the reviewed commit). Use
the kind "blocking" for a concrete defect with a failure scenario (questions 1, 2, 4 and 5);
everything else is advisory.
