dependencies:
	pip install -U pip
	pip install .
	pip install black

lint:
	black --check .

format-code:
	black .
