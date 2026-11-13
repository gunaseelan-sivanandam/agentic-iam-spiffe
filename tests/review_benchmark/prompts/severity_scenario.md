# Severity paragraph of the review benchmark's `open+list+sev`

The paragraph that the benchmark's configuration `open+list+sev` adds to the launcher's output section, after the `severity` bullet, for decision concern 8's measurement (step 3): candidate 1, "finish the scenario", of the author's severity analysis, verbatim. Everything else is `open+list`. The runner sends only the text under the heading below.

## Paragraph

Choose the severity from the end of the failure scenario, not its first symptom. Start from the reviewed commit as it stands and follow the scenario to what it lets reach the integration branch, the published evidence or a non-holder if nobody fixes it. The ends that matter: a requirement or decision left without a working proof; a test, gate or check that would pass while what it proves is broken, or whose failure would not stop the merge; a key, secret or token at a non-holder. A report that lists the gap, a failure under another job's name, or a reader who might notice is a symptom, not a stop. Something stops the problem only if you can point to it in the copy or the evidence: a test, a gate with the CI job that runs it, a required check. A finding with one of those ends is high at least, and blocking when it meets a blocking criterion.
