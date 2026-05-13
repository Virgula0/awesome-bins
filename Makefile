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
		--output type=local,dest=$(BUILD_CONTEXT)/bin_outputs \
		$(BUILD_CONTEXT)
.PHONY: build-container

check-compiled-versions:
	cat **/compiled_versions 2> /dev/null
.PHONY: clean-bins

clean-bins:
	rm -rf **/bins/**/* 2> /dev/null
.PHONY: clean-bins

check-bins:
	file **/bins/**/* 2> /dev/null
.PHONY: check-bins

.PHONY: create-module

.PHONY: create-module

# Define the template with placeholders
define PYTHON_TEMPLATE
from src.abstract import Module
from src.docker_custom import CustomClient
import requests  # type: ignore[import-untyped]
from pathlib import Path
import os


class $(shell echo $(NAME) | sed 's/.*/\u&/')(Module):
    _url = ""
    _target_name = "$(NAME)"
    _lts_file = os.path.join(Path(__file__).resolve().parent, "lts_version")
    _stable_file = os.path.join(
        Path(__file__).resolve().parent, "stable_working_version"
    )
    _compiled_file = os.path.join(Path(__file__).resolve().parent, "compiled_versions")
    _compose_file = os.path.join(Path(__file__).resolve().parent, "docker-compose.yaml")

    _verbose = False
    _docker_client = None

    _current_version = "0"
    _docker_env_version = "0"
    _stable_fallback_version = "0"

    def __init__(self, verbose, docker_client: CustomClient):
        super().__init__(verbose=verbose)
        self._verbose = verbose
        self._docker_client = docker_client

        self._current_version = self.read_version_from_file(self._lts_file)
        self._docker_env_version = f"$(shell echo $(NAME) | tr '[:lower:]' '[:upper:]')_VERSION={self._current_version}"

        self._stable_fallback_version = self.read_version_from_file(self._stable_file)

    def __str__(self):
        return self._target_name.upper()

    def update_version(self):
        try:
            pass
        except Exception as ex:
            print(ex)
            return False

        return True

    def _build(self, service):
        result = self._docker_client.run(
            service=service,
            compose_file=self._compose_file,
            version=self._docker_env_version,
        )

        if result:
            self.append_compiled(service=service, version=self._current_version)
            return result

        self.logger(
            f"ERROR for {service}! compilation not successful for version {self._current_version} "
            f"falling back and compile {self._stable_fallback_version}"
        )

        result = self._docker_client.run(
            service=service,
            compose_file=self._compose_file,
            version=f"$(shell echo $(NAME) | tr '[:lower:]' '[:upper:]')_VERSION={self._stable_fallback_version}",
        )

        if result:
            self.append_compiled(service=service, version=self._stable_fallback_version)

        return result

    def build_x86_64(self):
        return

    def build_x86(self):
        return

    def build_arm64(self):
        return

    def build_arm32(self):
        return
endef

export PYTHON_TEMPLATE

create-module:
	@if [ -z "$(NAME)" ]; then echo "Error: NAME is not set. Usage: make create-module NAME=netcat"; exit 1; fi
	@mkdir -p $(NAME)/bins/arm32 $(NAME)/bins/arm64 $(NAME)/bins/x86 $(NAME)/bins/x86_64
	@touch $(NAME)/bins/arm32/.gitkeep $(NAME)/bins/arm64/.gitkeep $(NAME)/bins/x86/.gitkeep $(NAME)/bins/x86_64/.gitkeep
	@touch $(NAME)/__init__.py
	@touch $(NAME)/compiled_versions
	@touch $(NAME)/docker-compose.yaml
	@touch $(NAME)/Dockerfile
	@touch $(NAME)/Dockerfile.arm32
	@touch $(NAME)/Dockerfile.arm64
	@touch $(NAME)/Dockerfile.x86
	@touch $(NAME)/lts_version
	@touch $(NAME)/stable_working_version
	@echo "$$PYTHON_TEMPLATE" > $(NAME)/$(NAME).py
	@echo "Module '$(NAME)' created successfully."
	@make format