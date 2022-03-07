install:
	poetry install

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl --force-reinstall

lint:
	poetry run flake8 page_loader

pre-commit-check:
	pre-commit run --all-files

run-tests:
	pytest

test-coverage:
	pytest --cov=page_loader --cov-report xml
