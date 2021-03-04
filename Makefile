SHELL=/bin/bash
PYTHON=python3
PIP=pip3
ACTIVATOR=source

requirements: clean env
	${ACTIVATOR} .virtualenv/bin/activate
	${PIP} install -e .

wheel:
	${PYTHON} setup.py sdist bdist_wheel

env:
	${PYTHON} -m venv .virtualenv
	${ACTIVATOR} .virtualenv/bin/activate
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

