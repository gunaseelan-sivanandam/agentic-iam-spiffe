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
MUTATION_MAX_CHILDREN ?= 2

.PHONY: unit unit-guard-check unit-invariants unit-boundary unit-negative-controls unit-hybrid-critical unit-flake unit-cov unit-diff-cov traceability-check unit-mutation unit-trust

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
