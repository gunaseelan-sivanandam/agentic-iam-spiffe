# RC-3: the author's answers to the earlier report

The answers section that the benchmark's recheck case RC-3 gives the reviewer, as the launcher would take it from a
review record. Its `fixed:` answer adds a process step (the summary written after CI and again after every push) where
leaving the CI result out of the summary would do (round 2 of slice 4, R2-10).

#### Answers to plan/c1/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| R1-1 | high | fixed: AGENTS.md: the summary is written once CI has finished on the PR's head commit, and written again after every later push, so its CI result is always the head's |
