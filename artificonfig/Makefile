.PHONY: help
.PHONY: init
.PHONY: install
.PHONY: dev
.PHONY: format
.PHONY: format-check
.PHONY: lint
.PHONY: test
.PHONY: doc
.PHONY: patch
.PHONY: minor
.PHONY: major
.PHONY: wheel
.PHONY: req-check

.SILENT: help
.SILENT: init

# Print all available commands
help:
	echo "	"
	echo "These are all the available commands you can execute with the 'make' command:"
	echo "	"
	echo "help  		to print all the possible commands"
	echo "init  		to create the git local and remote repository"
	echo "install		to install requirements without development dependencies"
	echo "dev   		to install requirements with development dependencies"
	echo "format 		to format the code with black tool"
	echo "format-check 	to check the formatting code with black"
	echo "lint  		to check the code style"
	echo "test  		to launch the tests"
	echo "req-check 	to check whether all required imports are in the requirements.txt file"
	echo "doc   		to create the project documentation"
	echo "patch  		to release a patch"
	echo "minor  		to release a minor version"
	echo "major  		to release a major version"
	echo "wheel  		to create a wheel to distribute this software"
	echo "	"

# Initialize the git local and remote repository
init:
	python -m utils.initialize

# Install requirements (development excluded)
install:
	pip install .

# Install all requirements (including development)
dev:
	pip install -e '.[dev]'
	pre-commit install

# Format the code with black tool
format:
	isort artificonfig tests utils
	black --fast --config=pyproject.toml artificonfig tests utils

# Check the formatting code with black
format-check:
	isort --check artificonfig tests utils
	black --check --config=pyproject.toml artificonfig tests utils

# Check the code style
lint:
	flake8 artificonfig tests utils

# Launch the tests
test:
	pytest -v --doctest-modules tests

# Create the project documentation
doc:
	python -m utils.autodocs artificonfig

# Release a patch
patch:
	python -m utils.release patch

# Release a minor version
minor:
	python -m utils.release minor

# Release a major version
major:
	python -m utils.release major

# Release a beta version
beta:
	python -m utils.release beta

# Release a stable version
stable:
	python -m utils.release stable

# Create a wheel (.whl file) inside dist directory
wheel:
	python -m build --wheel

# Check if all required imports are in the requirement file
req-check:
	python -m utils.requirement
