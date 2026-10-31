PYTEST ?= pytest
PYTHON ?= python3
MUTMUT ?= mutmut

TEST_DIR := tests/unit
COV_JSON := coverage.json
COV_XML := coverage.xml
MIN_TOTAL_LINE ?= 85
MIN_CRITICAL_BRANCH ?= 75
MIN_DIFF_COVERAGE ?= 90
MIN_MUTATION_SCORE ?= 70
BASE_REF ?= origin/main
# Gap gate: fail on a coverage gap the branch adds compared with its merge-base with BASE_REF.
# CI passes --mode pr --base origin/<PR base> on pull requests and --mode push on main.
QA_TRACE_ARGS ?= --mode pr --base $(BASE_REF)
# The main ruleset, readable without a token; gate-consistency compares its required checks with CI.
RULESET_URL ?= https://api.github.com/repos/gunaseelan-sivanandam/agentic-iam-spiffe/rulesets/26054924
MUTATION_MAX_CHILDREN ?= 2
# Everything a test run publishes (CI uploads exactly this); qa-evidence checks it for secrets.
PUBLICATION_SET := test_report.log artifacts/rogue-tests artifacts/quality

.PHONY: unit unit-guard-check unit-invariants unit-boundary unit-negative-controls unit-hybrid-critical unit-flake unit-cov unit-diff-cov traceability-check unit-mutation unit-trust qa-trace qa-evidence qa-quality docs-check tooling-test test-lint qa-deploy jira-live-smoke print-publication-set e2e gate-consistency

unit:
	$(PYTEST) $(TEST_DIR)

unit-guard-check:
	$(PYTEST) $(TEST_DIR)

unit-invariants:
	$(PYTEST) -m invariant $(TEST_DIR)

unit-boundary:
	$(PYTEST) -m boundary $(TEST_DIR)

unit-negative-controls:
	$(PYTEST) -m negative_control $(TEST_DIR)

unit-hybrid-critical:
	$(PYTEST) -m hybrid_critical $(TEST_DIR)

unit-flake:
	$(PYTEST) -m invariant --count=5 -q $(TEST_DIR)

unit-cov:
	$(PYTEST) \
	  --cov=services \
	  --cov-branch \
	  --cov-report=term-missing \
	  --cov-report=json:$(COV_JSON) \
	  --cov-report=xml:$(COV_XML) \
	  $(TEST_DIR)
	$(PYTHON) scripts/coverage_gate.py \
	  --coverage-json $(COV_JSON) \
	  --min-total-line $(MIN_TOTAL_LINE) \
	  --min-critical-branch $(MIN_CRITICAL_BRANCH)

unit-diff-cov: unit-cov
	./scripts/diff_coverage_gate.sh $(BASE_REF) $(MIN_DIFF_COVERAGE)

traceability-check:
	$(PYTHON) scripts/validate_unit_traceability.py \
	  --requirements docs/requirements.md \
	  --spec docs/unit_test_spec.md

unit-mutation:
	rm -rf mutants
	$(MUTMUT) run --max-children $(MUTATION_MAX_CHILDREN)
	$(MUTMUT) export-cicd-stats
	$(PYTHON) scripts/mutation_gate.py \
	  --stats mutants/mutmut-cicd-stats.json \
	  --min-score $(MIN_MUTATION_SCORE)

unit-trust: unit-guard-check unit-cov traceability-check unit-invariants unit-negative-controls unit-hybrid-critical unit-flake

qa-trace:
	$(PYTHON) scripts/validate_traceability.py \
	  --requirements-doc docs/requirements.md \
	  --architecture-doc docs/architecture.md \
	  --tests trace/tests.yaml \
	  --report-json artifacts/quality/traceability_report.json \
	  $(QA_TRACE_ARGS)

qa-evidence:
	$(PYTHON) scripts/validate_e2e_evidence.py \
	  --tests trace/tests.yaml \
	  --evidence-dir artifacts/rogue-tests \
	  --test-report test_report.log \
	  --report-json artifacts/quality/evidence_report.json \
	  --deploy-report artifacts/quality/qa_deploy_report.json \
	  --publication-set $(PUBLICATION_SET)

print-publication-set:
	@echo $(PUBLICATION_SET)

# Full E2E suite on the current stack state; run scripts/clean_stack.sh first for a clean run.
e2e:
	bash scripts/run_e2e.sh

qa-quality: qa-trace traceability-check unit-guard-check docs-check test-lint qa-deploy

docs-check:
	$(PYTHON) scripts/check_docs.py

test-lint:
	$(PYTHON) scripts/test_lint.py

# Locally the built images are inspected for their USER; CI passes QA_DEPLOY_ARGS=--skip-image-users.
qa-deploy:
	$(PYTHON) scripts/qa_deploy.py $(QA_DEPLOY_ARGS)

gate-consistency:
	$(PYTHON) scripts/check_gate_consistency.py --ruleset-url $(RULESET_URL)

tooling-test:
	$(PYTEST) -q tests/tools
	bash tests/shell/test_varambu_output.sh

jira-live-smoke:
	./scripts/jira_live_smoke.sh
