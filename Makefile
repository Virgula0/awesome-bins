# Default variables for local builds
CACHE_ARGS ?=

install-requirements:
	pip install -r requirements.txt
.PHONY: install-requirements

# Install linting tools
install-lint:
	pip install ruff black mypy
.PHONY: install-lint

# Run all linters against the entire project
lint:
	ruff check .
	black --check .
	mypy .
.PHONY: lint

# Auto-fix formatting issues
format:
	black .
	ruff check . --fix
.PHONY: format

setup-docker:
	docker run --privileged --rm tonistiigi/binfmt --install all
	docker buildx create --use --name multiarch
	docker buildx inspect --bootstrap
.PHONY: setup-docker

# Command for CI for optimized local builds
build-container:
	docker buildx build $(CACHE_ARGS) \
		--platform linux/amd64,linux/arm64 \
		-t my-compiler-output:latest \
		--output type=local,dest=./bin_outputs \
		.
.PHONY: build-container

clean-bins:
	rm -rf **/bins/**/* 2> /dev/null
.PHONY: clean-bins

check-bins:
	file **/bins/**/* 2> /dev/null
.PHONY: check-bins