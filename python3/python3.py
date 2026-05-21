from src.abstract import Module
from src.docker_custom import CustomClient
from pathlib import Path
import re
import requests as r
import os


class Python3(Module):
    _url = "https://raw.githubusercontent.com/python/cpython/main/Include/patchlevel.h"
    _target_name = "python3"
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
        self._docker_env_version = f"PYTHON3_VERSION={self._current_version}"

        self._stable_fallback_version = self.read_version_from_file(self._stable_file)

    def __str__(self):
        return self._target_name.upper()

    def update_version(self):
        try:
            response = r.get(self._url, timeout=10)
            response.raise_for_status()
            content = response.text

            major = re.search(r"#define PY_MAJOR_VERSION\s+(\d+)", content)
            minor = re.search(r"#define PY_MINOR_VERSION\s+(\d+)", content)
            micro = re.search(r"#define PY_MICRO_VERSION\s+(\d+)", content)

            if not (major and minor and micro):
                self.logger("Could not parse version components from patchlevel.h")
                return False

            version = f"{major.group(1)}.{minor.group(1)}.{micro.group(1)}"
            self.logger(f"Latest Python version: {version}")

            with open(self._lts_file, "w") as f:
                f.write(f"{version}")

            self._current_version = version
            self._docker_env_version = f"PYTHON3_VERSION={self._current_version}"

            return True

        except Exception as e:
            self.logger(f"Error: {e}")
            return False

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
            version=f"PYTHON3_VERSION={self._stable_fallback_version}",
        )

        if result:
            self.append_compiled(service=service, version=self._stable_fallback_version)

        return result

    def build_x86_64(self):
        """
        PYTHON3_VERSION=3.16.0 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up python3-static-build-x86_64 --build
        """
        return self._build("python3-static-build-x86_64")

    def build_x86(self):
        """
        PYTHON3_VERSION=3.16.0 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up python3-static-build-x86 --build
        """
        return self._build("python3-static-build-x86")

    def build_arm64(self):
        """
        PYTHON3_VERSION=3.16.0 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up python3-static-build-arm64 --build
        """
        return self._build("python3-static-build-arm64")

    def build_arm32(self):
        """
        PYTHON3_VERSION=3.16.0 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up python3-static-build-arm32 --build
        """
        return self._build("python3-static-build-arm32")

