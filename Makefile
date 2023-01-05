dependencies:
	pip install -U pip
	pip install .
	pip install -r requirements.txt

lint:
	ruff .
	isort --check .

format-code:
	black .
	isort .