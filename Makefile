doc:
	pip install testinstances[docs]
	cd doc/ && make html

lint:
	pip install --use-mirrors testinstances[lint]
	pyflakes ./testinstances
	pyflakes ./tests
	pep8 ./testinstances./tests

test:
	pip install testinstances[test]
	python setup.py nosetests --cover-package=testinstances

vendor:
	make -C vendor


.PHONY: doc unit integration test lint vendor
