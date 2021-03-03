SHELL=/bin/bash
PYTHON=python3
PIP=pip

requirements: clean env
	. .virtualenv/bin/activate
	${PIP} install -e .

wheel:
	${PYTHON} setup.py sdist bdist_wheel

env:
	${PYTHON} -m venv .virtualenv
	. .virtualenv/bin/activate
	${PIP} install --upgrade wheel pip

clean:
	rm -rf .virtualenv
	rm -rf build
	rm -rf dist
	rm -rf irida_staramr_results.egg-info/

help:
	@echo "---------------HELP-----------------"
	@echo "To install and build project from source code, type: make"
	@echo "------------------------------------"

