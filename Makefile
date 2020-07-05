venv: FORCE
	python3 -m venv ./venv/
	echo ./venv/bin/activate
	. ./venv/bin/activate && pip3 install -r requirements.txt

clean: FORCE
	find . -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -exec rm {} +
	rm -rf ./venv

lint:
	. ./venv/bin/activate && isort --force-alphabetical-sort-within-sections --force-single-line-imports --virtual-env venv --reverse-relative DockerENT
	. ./venv/bin/activate && pylama DockerENT

FORCE: