# RC-4: the author's answers to the earlier report

The answers section that the benchmark's recheck case RC-4 gives the reviewer, as the launcher would take it from a
review record. Its `rejected:` answer cites a real test, which passes, but whose fixture writes the header without a
code span, so it does not cover the finding's scenario (round 2 of slice 4, R2-10).

#### Answers to implementation/c1/r1/A/1

| ID | Severity | Answer |
| --- | --- | --- |
| R1-1 | high | rejected: the credential rule still finds a bearer token: tests/tools/test_evidence_secrets.py::test_each_secret_shape_is_found runs the fixture "Authorization Bearer header" (tests/tools/test_evidence_secrets.py:86), which still passes with this change, and test_finding_names_file_and_kind_never_the_value checks the same fixture through scan |
