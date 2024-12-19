# Common variables
PYTHON=python
PACKAGE_DIR = rqto
TEST_DIR = testing

TEST_CMD = ${PYTHON} testing/manage.py test --parallel
TEST_WARNINGS_CMD = ${PYTHON} -Wa manage.py test
# see .coveragerc for settings
COVERAGE_CMD = coverage run testing/manage.py test --noinput && coverage xml && coverage report
STATIC_CMD = ruff check .
VULN_STATIC_CMD = bandit -r -ii -ll -x ${PACKAGE_DIR}/migrations ${PACKAGE_DIR} 
FORMAT_CMD = ruff format .
FORMATCHECK_CMD = ${FORMAT_CMD} --check


install:
	pip install --upgrade pip .[dev]
.PHONY: install

format:
	${FORMAT_CMD}
.PHONY: format

static-fix:
	${STATIC_CMD} --fix
.PHONY: static-fix

# Test targets

test-all: coverage static vuln-static formatcheck
.PHONY: test-all

test:
	${TEST_CMD}
.PHONY: test

test-warnings:
	${TEST_WARNINGS_CMD}
.PHONY: test-warnings

coverage:
	${COVERAGE_CMD}
.PHONY: coverage

static:
	${STATIC_CMD}
.PHONY: static

vuln-static:
	${VULN_STATIC_CMD}
.PHONY: vuln-static

formatcheck:
	${FORMATCHECK_CMD}
.PHONY: formatcheck
