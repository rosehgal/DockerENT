venv: FORCE
	python3 -m venv ./venv/
	echo ./venv/bin/activate
	. ./venv/bin/activate && pip3 install -r requirements.txt

clean: FORCE
	find . -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -exec rm {} +
	rm -rf ./venv

lint:
	pylama DockerENT

FORCE: