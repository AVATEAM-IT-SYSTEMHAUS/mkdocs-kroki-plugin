dependencies:
	pip install -U pip
	pip install .
	pip install -r requirements.txt

lint:
	ruff .
	black --check .

format-code:
	black .
	ruff --fix .
