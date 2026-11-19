# Research: defining and measuring the reliability of the PoC's agents

This note collects published practice on what "reliable" means for an LLM agent and how it is measured,
how agent roles are defined so that every start gets the same agent, how agents that author artifacts
(not only reviewers) are evaluated, and what a proportionate bar is for this PoC under its delivery threat
model (honest agent mistakes, no deliberate attacks, no production hardening; `AGENTS.md`, "PoC scope and
proportion"). It is input for the owner's definition of the PoC goal's word "reliable"
(`docs/slices/agentic-sdlc-poc/plan.md`, Goal), which was never defined or measured. Every external claim
carries a source URL and a short verbatim quote, as returned by the fetch tool on 2026-11-19. Numbers marked
"calculation" are this note's own (method in [Calculations](#calculations)). Nothing here is approved; every
measurement or step it recommends is a process addition the owner decides under "Ask before growing".

## 1. How the reliability of an LLM agent is defined and measured

### Reliability is consistency over repeated runs, not one success

- One run is not a measurement: agent output varies between runs, so evals run several trials per task.
  "Regardless of agent type, agent behavior varies between runs." / "Because model outputs vary between
  runs, we run multiple trials to produce more consistent results."
  ([Anthropic, Demystifying evals for AI agents, 2026-01-09](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents))
- Two metrics, two meanings. pass@k: "the likelihood that an agent gets at least one correct solution in k
  attempts"; pass^k: "the probability that all k trials succeed"; "which to use depends on product
  requirements." ([Anthropic, same](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents))
- pass^k was introduced to measure reliability, and it exposes inconsistency that pass@1 hides: "We also
  propose a new metric (pass^k) to evaluate the reliability of agent behavior over multiple trials." / agents
  "succeed on <50% of the tasks" and are inconsistent "(pass^8 <25% in retail)."
  ([τ-bench, arXiv 2406.12045](https://arxiv.org/abs/2406.12045))
- pass^k falls fast: "with a 75% per-trial success rate and 3 trials, the probability of passing all three is
  (0.75)³ ≈ 42%." ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).
  Calculation: per-run 0.9 gives pass^3 = 0.73; 0.8 gives 0.51; 0.7 gives 0.34.
- For a delivery process, where every stage must catch its defects every time, the relevant reading is pass^k
  (each start of the role works), not pass@k (some start works). This is an inference, not a quote.
- Anthropic lists consistency as its own success criterion: "How similar do the model's responses need to be
  for similar types of input? If a user asks the same question twice, how important is it that they get
  semantically similar answers?"
  ([Claude Docs, Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/define-success))

### Success criteria come first and must be measurable

- "Specific: Clearly define what you want to achieve." / "Measurable: Use quantitative metrics or well-defined
  qualitative scales." / "Achievable: Base your targets on industry benchmarks, prior experiments, AI research,
  or expert knowledge." ([Claude Docs, Define success](https://platform.claude.com/docs/en/test-and-evaluate/define-success))
- "Most use cases need multidimensional evaluation along several success criteria." (same) For a reviewer
  this means at least detection (misses) and false alarms, reported separately.
- A good case is unambiguous: "A good task is one where two domain experts would independently reach the same
  pass/fail verdict." / "For each task, it's useful to create a reference solution: a known working output
  that passes all graders." ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents))
- Balanced sets: "Test both the cases where a behavior should occur and where it shouldn't." / "One-sided evals
  create one-sided optimization." (same) Slice 4's benchmark already had clean cases and a decoy.
- Start small, from real failures: "20-50 simple tasks drawn from real failures is a great start." (same)
- Capability versus regression: regression evals "should have a nearly 100% pass rate." (same) A frozen set
  the shipped role must keep passing is a regression eval; a set used to compare wordings is a capability eval.
- Isolation: "Each trial should be "isolated" by starting from a clean environment." (same)
- Read transcripts: "You won't know if your graders are working well unless you read the transcripts and grades
  from many trials." / "a 0% pass rate across many trials" is "most often a signal of a broken task, not an
  incapable agent." (same)

### Statistics: error bars, pairing, repeats and power

- Report an interval with every score: "we encourage researchers to report the SEM, derived from the Central
  Limit Theorem, alongside each calculated eval score."
  ([Anthropic, A statistical approach to model evaluations, 2024-11-19](https://www.anthropic.com/research/statistical-approach-to-model-evals);
  paper [arXiv 2411.00640](https://arxiv.org/abs/2411.00640))
- Correlated cases: "we recommend clustering standard errors on the unit of randomization." (same) Here,
  several planted defects in one file or one slice are one cluster, not independent cases.
- Repeats reduce noise: "we recommend resampling answers from the same model several times." / "Going from
  K=1 (no resampling of answers) to K=2, the total variance is reduced by 1/3." (same; paper §3.1)
- Comparing two setups on the same cases: "conducting a paired-differences test lets us eliminate the variance
  in question difficulty." (same) Pairing helps only "as long as the conditional means of the model scores are
  correlated." ([arXiv 2411.00640 §4.2](https://arxiv.org/html/2411.00640))
- Power analysis before running: the post shows how to "calculate the number of questions that an eval should
  have in order to test this hypothesis"; the paper's Equation 9 gives "the number of independent questions n
  required" for a chosen error rate, and suggests new evals "should contain at least 1,000 questions in order to
  have good signaling ability." ([post](https://www.anthropic.com/research/statistical-approach-to-model-evals),
  [paper §5](https://arxiv.org/html/2411.00640))
- What this means at this repository's sizes (calculation, exact tests, two-sided α = 0.05, 80% power, paired
  binary outcomes per case):

  | True detection rates of setup A vs B | Assumed share of cases where they disagree | Paired cases needed | Power at 15 cases (slice 4's size) |
  | --- | --- | --- | --- |
  | 50% vs 90% | 40%, all one way | about 19 | 0.60 |
  | 60% vs 80% | 20%, all one way | about 39 | 0.06 |
  | 60% vs 80% | 30% (25% vs 5%) | about 61 | 0.09 |
  | 70% vs 80% | 20% (15% vs 5%) | about 168 | 0.01 |

  This is why 7 of 8 wording comparisons in slice 4 were within chance (DPL-016): at 15 cases with one run each,
  only a difference of about 40 points has a fair chance of showing. The repository's own research already said
  so ([`industry_research.md`](../../../docs/slices/agentic-sdlc-poc/industry_research.md), row 6: "About 15 cases
  with one run each screen for large effects only").
- An absolute bar is far cheaper than a comparison. Rule of three: if an event "did not occur in a sample with n
  subjects," then "the interval from 0 to 3/n is a 95% confidence interval for the rate of occurrences in the
  population." ([Wikipedia, Rule of three (statistics)](https://en.wikipedia.org/wiki/Rule_of_three_(statistics)))
  Calculation (exact one-sided 95% upper bound on the miss rate below a target):

  | Target miss rate | 0 misses | 1 miss | 2 misses |
  | --- | --- | --- | --- |
  | < 30% | 9 cases | 14 cases | 19 cases |
  | < 20% | 14 cases | 22 cases | 30 cases |
  | < 10% | 29 cases | 46 cases | 61 cases |

- Width of an observed rate (calculation, exact 95% interval for an observed 80%): 15 cases [0.52, 0.96];
  20 cases [0.56, 0.94]; 30 cases [0.61, 0.92]; 50 cases [0.66, 0.90].

### Seeded defects and mutation-style testing of reviewers

- Defect seeding ("bebugging"): "Known bugs are randomly added to a program's source code and the software tester
  is tasked to find them." / "The percentage of the known bugs not found gives an indication of the real bugs that
  remain." Limitation: "we cannot introduce program bugs which simulate real bugs."
  ([Wikipedia, Bebugging](https://en.wikipedia.org/wiki/Bebugging))
- Synthetic defects are criticised for the same reason in AI code-review benchmarks: "no evidence that synthetic
  bugs match the distribution or subtlety of real defects"; ground truth should come from "CVE databases, bug-fix
  commits, or human-validated defects, not synthetic ones"; "Anything under 100 entries should be treated with
  skepticism"; "Self-evaluation is biased, even in good faith."
  ([DeepSource, AI code review benchmarks](https://deepsource.com/blog/ai-code-review-benchmarks); a vendor's
  critique of other vendors, so read it as an argument, not as data)
- False alarms are a measured failure, and longer prompts can raise them: LLMs "frequently misclassify correct
  code implementation as non-compliant or defective"; "more detailed prompt design, particularly with those
  requiring explanations and proposed corrections" "leads to higher misjudgment rates."
  ([Jin & Chen, Are LLMs Reliable Code Reviewers?, arXiv 2603.00539](https://arxiv.org/abs/2603.00539)) Relevant to
  the review mandates, which ask for evidence and consequences.
- Senior-practitioner reading: report the miss rate on defect cases and the false-alarm (or false-blocker) rate on
  clean cases separately, and prefer real past misses (slice 4's RM cases) over plants, because plants skew easy.

### Agreement with human experts

- LLM judges reach human-level agreement on some tasks: "over 80% agreement, the same level of agreement between
  humans." ([Zheng et al., Judging LLM-as-a-judge, arXiv 2306.05685](https://arxiv.org/abs/2306.05685))
- Cohen's kappa corrects agreement for chance: "If there is no agreement among the raters other than what would be
  expected by chance (as given by pe), κ=0." The usual bands ("0.61–0.80 as substantial") "are however by no means
  universally accepted", and "kappas are higher when codes are equiprobable."
  ([Wikipedia, Cohen's kappa](https://en.wikipedia.org/wiki/Cohen%27s_kappa))
- With rare failures, raw agreement misleads; treat the judge as a classifier: "agreement can be misleading when
  failures are rare" / "Treat the judge as a binary classifier." (true and false positive rates)
  ([Husain, Using LLM-as-a-judge](https://hamel.dev/blog/posts/llm-judge/))

## 2. Defining agent roles so that every start gets the same agent

- Versioned, project-scoped definitions: "Project subagents (`.claude/agents/`) are ideal for subagents specific to
  a codebase. Check them into version control so your team can use and improve them collaboratively."
  ([Claude Code docs, Subagents](https://code.claude.com/docs/en/sub-agents))
- The definition can pin what varies: `model` ("a full model ID such as `claude-opus-5-5`, or `inherit`. When you
  omit it, Claude Code picks the model in the subagent model order"), `tools`, `disallowedTools`, `effort` ("Overrides
  the session effort level, but not the `CLAUDE_CODE_EFFORT_LEVEL` environment variable"), `maxTurns`, `skills`
  ("The full skill content is injected"), `hooks`, `permissionMode`. (same) Two consequences: omit no field that
  varies between starts (model, effort), and note that an environment variable can still change effort.
- Same-named definitions shadow each other: "When multiple subagents share the same name, Claude Code uses the one
  from the higher-priority location"; managed settings and the `--agents` flag rank above `.claude/agents/`. (same)
- A subagent started with the Agent tool receives only what its caller writes: "The only content you pass from
  parent to subagent is the Agent tool's prompt string, so include any file paths, error messages, or decisions the
  subagent needs directly in that prompt." ([Agent SDK docs, Subagents in the SDK](https://code.claude.com/docs/en/agent-sdk/subagents))
  So a subagent file fixes the role's system prompt, tools and model, but not its inputs: the caller still chooses
  them. That is the gap `scripts/run_independent_review.py` closes for the reviewer (inputs computed by
  `scripts/review_inputs.py`, mandate SHA-256 recorded per attempt).
- Two documented ways to have a tool, not the caller, compute inputs: a script that builds the prompt (the launcher
  pattern) or a skill's shell injection: "The `` !`<command>` `` syntax runs shell commands before the skill content is
  sent to Claude. The command output replaces the placeholder, so Claude receives actual data, not the command
  itself." A skill with `context: fork` runs as a subagent: "The subagent doesn't see your conversation history, so the
  skill's instructions have to stand on their own." ([Claude Code docs, Skills](https://code.claude.com/docs/en/skills))
- Reproducible headless starts: without `--bare`, `claude -p` "discovers and loads" hooks, skills, subagents, plugins,
  MCP servers, memory and CLAUDE.md "as an interactive session would, including anything configured in the working
  directory or `~/.claude`." "Bare mode is useful for CI and scripts where you need the same result on every machine."
  "`--bare` is the recommended mode for scripted and SDK calls, and will become the default for `-p` in a future
  release." Context is then passed explicitly (`--append-system-prompt-file`, `--settings`, `--agents`). Constraint:
  "In bare mode, Claude Code never reads OAuth credentials or the system keychain" (an API key is needed).
  ([Claude Code docs, Run Claude Code programmatically](https://code.claude.com/docs/en/headless))
- Structured output: "use `--output-format json` with `--json-schema` … with the structured output in the
  `structured_output` field." "If a run ends without valid structured output … the response has no
  `structured_output` field. Before your script uses `structured_output`, check that the field is present." (same)
  A schema makes findings, severities and `accounted` rows machine-checkable instead of parsed from prose.
- Programmatic definitions are the SDK's recommended form ("This guide focuses on the programmatic approach, which
  is recommended for SDK applications") and override files: "Programmatically defined agents take precedence over
  filesystem-based agents with the same name." ([Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/subagents))
- Practice this implies (inference): one definition per role, in the repository, reviewed like code; the full model
  ID and effort pinned; inputs computed by a script; output against a schema; and every run records the definition's
  hash, the model ID and the CLI version (slice 4's canary already gated on the CLI version). A role whose definition,
  model or CLI changes reruns its frozen regression set.

## 3. Evaluating agents that author artifacts

- Grade outcomes with deterministic graders where possible: "Deterministic graders are natural for coding agents";
  "coding evaluations typically rely on unit tests for correctness verification"; in SWE-bench "a solution passes only
  if it fixes the failing tests without breaking existing ones"; "it's often better to grade what the agent produced,
  not the path it took." ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents))
- Choose the grader in this order: "Code-based grading: Fastest and most reliable"; "Human grading: Most flexible and
  high quality, but slow and expensive. Avoid if possible."; "LLM-based grading: … Test to ensure reliability first,
  then scale." ([Claude Docs, Define success](https://platform.claude.com/docs/en/test-and-evaluate/define-success))
- Generated tests are filtered by deterministic checks before anyone trusts them: "75% of TestGen-LLM's test cases
  built correctly, 57% passed reliably, and 25% increased coverage"; "73% of its recommendations being accepted for
  production deployment by Meta software engineers."
  ([Meta, Automated Unit Test Improvement using LLMs, arXiv 2402.09171](https://arxiv.org/abs/2402.09171)) The
  repository's gates (a new test fails on the base code, `make unit-mutation`, `make test-lint`, `make qa-trace`) are
  this kind of grader for the tests-first and implementation stages.
- Rubrics per case for open-ended artifacts: "Responses are evaluated using conversation-specific rubrics created by
  262 physicians" with "48,562 unique rubric criteria."
  ([HealthBench, arXiv 2505.08775](https://arxiv.org/abs/2505.08775)); "create clear, structured rubrics to grade each
  dimension of a task" and "For tasks with multiple components, build in partial credit."
  ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)); "Have detailed, clear
  rubrics"; "Be empirical or specific"; "Encourage reasoning" with thinking on.
  ([Claude Docs](https://platform.claude.com/docs/en/test-and-evaluate/define-success))
- LLM-as-judge biases: "position, verbosity, and self-enhancement biases" and "limited reasoning ability."
  ([Zheng et al.](https://arxiv.org/abs/2306.05685)); "Position bias (response order), verbosity bias (preferring
  longer responses)"; "Use pairwise comparison or pass/fail for more reliability"
  ([OpenAI, Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices));
  self-enhancement matters here because the author, reviewer and any judge are all Claude.
- Calibrate the judge against the human expert, then scale: "LLM-as-judge graders should be closely calibrated with
  human experts" ([Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)); "Use human
  feedback to calibrate automated scoring." / "Once the LLM judge reaches a point where it's faster, cheaper, and
  consistently agrees with human annotations, scale up" ([OpenAI](https://developers.openai.com/api/docs/guides/evaluation-best-practices));
  "LLM-generated evaluators simply inherit all the problems of the LLMs they evaluate, requiring further human
  validation." ([Shankar et al., Who Validates the Validators?, arXiv 2404.12272](https://arxiv.org/abs/2404.12272))
- One expert is normal, and binary verdicts beat scales: "there is usually one (maybe two) key individuals whose
  judgment is crucial"; "Just a clear pass or fail decision."; "People don't know what to do with a 3 or 4."
  ([Husain](https://hamel.dev/blog/posts/llm-judge/)) In this PoC the owner is that expert.
- Criteria drift: "users need criteria to grade outputs, but grading outputs helps users define criteria."
  ([Shankar et al.](https://arxiv.org/abs/2404.12272)) Expect the owner's rubric to change after the first graded
  outputs; freeze it before the measured run, not before the first look.
- Keep cases out of the prompt and hold a test split: "Dev set examples must stay out of the prompt." / "Never place
  dev or test examples in the judge prompt." / "Freeze the prompt, run the judge on the test set once."
  ([Husain](https://hamel.dev/blog/posts/llm-judge/)) The same rule applies to role prompts: text measured by a case
  must not be written from that case (the author's own lesson after slice 4).
- How many labels: "I start with around 30 examples and keep going until I do not see any new failure modes." / "Aim
  for about 100 examples per failure mode" / "Below 60 examples, the confidence intervals are often too wide to
  support a useful conclusion." ([Husain](https://hamel.dev/blog/posts/llm-judge/))
- Mine real cases: "Log everything: Log as you develop so you can mine your logs for good eval cases."; anti-pattern
  "Vibe-based evals: Using "it seems like it's working" as an evaluation strategy."
  ([OpenAI](https://developers.openai.com/api/docs/guides/evaluation-best-practices)) This repository already logs every
  review attempt and finding (`review_attempts.jsonl`, review records), so authoring-stage defects found by later
  stages are a ready source of real cases with an origin stage.

## 4. A proportionate bar and measurement for this PoC

What the threat model needs (inference from the sources above and `AGENTS.md`):

- The failure to measure is an honest miss or false alarm by a role, so each role needs a miss rate on defect
  cases, a false-alarm rate on clean cases and a consistency figure across starts. Deliberate evasion
  (adversarial cases, prompt injection against the reviewer) is outside the delivery threat model.
- The decision the owner needs is "is this role good enough to rely on", not "is wording A better than wording B".
  The first is an absolute, one-sided bar that 20 to 30 cases can decide; the second needs 40 to 170 paired cases
  for the effect sizes slice 4 saw (calculation above). So: choose wordings by research and reasoning, and measure
  the shipped role against a bar.
- Every outcome of a measurement must map to a decision before it runs (pass the bar, or do not pass and fix the
  role), so that "within chance" cannot be the result. This is a pre-registration of the bar, n and k; the power
  table is the check that the bar can be decided.

Production weight to leave out, and why:

| Practice | Source | Why it is out for the PoC |
| --- | --- | --- |
| Eval sets of 1,000 or more items | "at least 1,000 questions" ([paper §5](https://arxiv.org/html/2411.00640)) | Built to detect small differences between models; the PoC needs to decide an absolute bar, which 20 to 30 cases can |
| 100 or more labelled items per failure mode, kappa with tight intervals | ([Husain](https://hamel.dev/blog/posts/llm-judge/)), ([DeepSource](https://deepsource.com/blog/ai-code-review-benchmarks)) | Needs an annotation team; the owner is the single expert, and no LLM judge needs to be a gate if deterministic gates and the owner grade the outcomes |
| Continuous evaluation on every change | "run evals on every change" ([OpenAI](https://developers.openai.com/api/docs/guides/evaluation-best-practices)) | Cost per change; rerun only when a role's definition, model ID or CLI version changes |
| Independent third-party benchmark, published dataset | ([DeepSource](https://deepsource.com/blog/ai-code-review-benchmarks)) | Guards vendor bias in public claims; the PoC's claims are internal to the owner |
| Capture-recapture estimates of residual defects | inspection literature (not read in full, see Gaps) | Estimates defects left in a product; the PoC needs per-role detection, not a residual count |
| Adversarial robustness of the reviewer | (none needed) | Outside the delivery threat model (OPL-009 accepts the residual) |

## Recommended measurement for the PoC

Per agent role (the reviewer now; each authoring role once it has a definition). Numbers come from the
calculations above; the cost assumes slice 4's observed cost of about USD 0.67 per reviewer call (105 calls,
about USD 70, DPL-016).

1. **Frozen case set per role, hashed before any run:** 20 defect cases and 10 clean cases (at least 2 of them
   decoys). At least half of the defect cases are real past misses from the repository's review records, not
   plants; no case shapes the role's prompt text; cases from the same file or slice are counted as a cluster.
2. **Bar, decided one-sided at 95%:** at most 2 misses in 20 shows a miss rate below 30% (19 cases suffice);
   0 false blockers in 10 clean cases shows a false-blocker rate below 26%. Any other outcome is "bar not met":
   read the transcripts, fix the role, rerun. A tighter bar (below 20% with at most 2 misses) needs 30 defect
   cases; below 10% needs 46 to 61 and is out of budget.
3. **Consistency:** 3 runs on each of 10 of those cases (5 defect, 5 clean), 20 extra runs; report pass^3 per
   case and every case whose verdict flips between runs. With 10 cases this is descriptive, not a decided bar.
4. **Authoring roles:** the grader is the outcome, by the existing deterministic gates first (the artifact passes
   its stage's checks; a new test fails on the base code; mutants are killed), then the independent review's
   round-1 blocking, high and medium findings per review unit, taken from the attempt logs at no extra run cost.
   For the frozen set, about 10 tasks per role from past slices with a reference solution, 3 runs each (30 runs);
   the owner grades pass or fail on a sample where no gate decides.
5. **Rerun trigger:** the frozen set reruns when a role's definition hash, model ID or CLI version changes.
6. **No wording A/B** unless the expected difference is about 40 points or more (about 20 paired cases); a
   20-point difference needs about 40 to 60 paired cases and is out of PoC budget.

Budget per role: about 50 runs (30 + 20), about USD 34, for the reviewer; about 30 to 50 runs for an authoring
role. Each of these is a process addition the owner approves or rejects.

## Calculations

Exact methods, standard library only, run on 2026-11-19 (script kept outside the repository): one-sided and
two-sided Clopper-Pearson bounds by bisection on the binomial distribution; power of the exact two-sided McNemar
test by enumerating the number of discordant cases and the split between them. The paired-case counts depend on
the assumed share of cases where the two setups disagree, which is not known for this repository; slice 4's results
(`docs/slices/poc-4-5-benchmark/benchmark_results_B.jsonl`) could estimate it but were not analysed here. Exact
tests have sawtooth power, so "about" applies to every paired count.

## Gaps: what this research did not find or could not verify

- Quotes were extracted by the fetch tool's summarising model, not copied by hand; a quote that a decision rests on
  should be spot-checked on its page.
- No published guidance was found on how many cases and repeats are needed to estimate pass^k for agents, or on
  measuring agents that author requirements or architecture documents; the recommendations for those roles are
  inference from coding-agent and judge practice.
- The OpenAI HealthBench page returned HTTP 403; its abstract does not report how its model grader agreed with
  physicians, so the rubric-grading evidence is the rubric design only.
- Mills' original seeding paper and the capture-recapture inspection studies were not read; seeding is cited only
  from a secondary source (Wikipedia).
- Vendor code-review benchmark figures (recall and precision by tool) appeared in search results but were not
  verified against primary sources and are not used.
- Anthropic's docs also state an eval principle on volume versus hand-graded quality; that passage was not fetched
  in this session and is not quoted.
- Not checked: whether Claude Code lets a caller fix sampling temperature or a seed (if not, repeats are the only
  handle on variance); whether `--bare` fits the owner's login setup (it needs an API key); how `--bare` compares
  with the launcher's present confinement of the reviewer.
- The paired power figures rest on assumed disagreement rates; a kappa sample-size calculation for owner-versus-judge
  agreement was not done.
