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