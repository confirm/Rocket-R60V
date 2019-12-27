#
# Cleanup
#

clean:
	rm -vrf .venv build dist .eggs *.egg-info hactar/server/static
	find . -name '__pycache__' -delete

#
# Install
#

venv:
	python3 -m venv .venv

develop:
	pip install -r requirements-dev.txt
	pip install -e .

install:
	pip install .

#
# Test
#

test-pycodestyle:
	curl -so tox.ini https://git.confirm.ch/confirm/code-analysis/raw/master/tox.ini
	pycodestyle rocket-r60v
	pycodestyle rocket_r60v

test-pylint:
	curl -so .pylintrc https://git.confirm.ch/confirm/code-analysis/raw/master/pylintrc
	pylint rocket-r60v
	find rocket_r60v -maxdepth 2 -type f -name '__init__.py' -exec dirname {} \; | xargs pylint

test-unittest:
	python -munittest discover

test: test-pycodestyle test-pylint test-unittest

#
# Build
#

build:
	./setup.py sdist

upload-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload:
	twine upload dist/*