# RC-2: the author's answers to the earlier report

The answers section that the benchmark's recheck case RC-2 gives the reviewer, as the launcher would take it from a
review record. Both answers hold: the `rejected:` answer's reason checks out in the files it cites, and the `fixed:`
answer's change is in the file it names (decision concern 4, the owner's decision of 2026-11-13).

#### Answers to implementation/c1/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| R1-1 | high | rejected: only outcome guards are linted. parse_guards in scripts/test_lint.py (line 108) collects a guard only when its logical line, with backslash continuations joined, starts with `outcome_guard`; the four `\|\| :` lines are continuations of `exercise_guard` commands that capture container logs (scripts/rogue_node_tests.sh:3068-3069, 3117-3118, 3418-3419 and 3559-3560), so the lint never checks them. tests/tools/test_test_lint.py::test_or_colon_in_exercise_plumbing_passes shows that an exercise guard ending in `\|\| :` passes, and test_current_harness_is_clean lints the current harness |
| R1-2 | blocking | fixed: tests/tools/test_test_lint.py: test_each_loose_pattern_is_flagged gains guards ending in `\|\| :`, `\|\|:` and `\|\|true`, each flagged as or-true, and two new tests show that `\|\| :` inside a command substitution and in an exercise guard still passes, as `\|\| true` does |
