.PHONY: help
.PHONY: init
.PHONY: install
.PHONY: dev
.PHONY: format
.PHONY: format-check
.PHONY: lint
.PHONY: lint-fix
.PHONY: test
.PHONY: tree
.PHONY: doc
.PHONY: patch
.PHONY: minor
.PHONY: major
.PHONY: wheel

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
	echo "format 		to format the code with ruff tool"
	echo "format-check 	to check the formatting code with ruff"
	echo "lint  		to check the code style"
	echo "lint-fix 		to check and fix the code style"
	echo "test  		to launch the tests"
	echo "tree  		to print the structure of the repository ignoring what is declared in .gitignore"
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

# Format the code with ruff tool
format:
	ruff format minimamba tests utils

# Check the formatting code with ruff
format-check:
	ruff format --check minimamba tests utils

# Check code style
lint:
	ruff check minimamba tests utils

# Fix code style
lint-fix:
	ruff check --fix minimamba tests utils

# Launch the tests
test:
	pytest -v --doctest-modules tests

# Print the structure of the repository ignoring what is declared in .gitignore
tree:
	python -m utils.tree

# Build and visualize documentation through a local server
doc:
	mkdocs build
	mkdocs serve

# Release a patch
patch:
	python -m utils.release patch

# Release a minor version
minor:
	python -m utils.release minor

# Release a major version
major:
	python -m utils.release major

# Create a wheel (.whl file) inside dist directory
wheel:
	python -m build --wheel
