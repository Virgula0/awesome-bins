from src.abstract import Module
from src.docker_custom import CustomClient
from pathlib import Path
import os
import requests as r
import re


class Gcc(Module):
    _url = "https://api.github.com/repos/gcc-mirror/gcc/branches?per_page=1000"
    _target_name = "gcc"
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
        self._docker_env_version = f"GCC_VERSION={self._current_version}"

        self._stable_fallback_version = self.read_version_from_file(self._stable_file)

    def __str__(self):
        return self._target_name.upper()

    def update_version(self):
        try:
            response = r.get(self._url, timeout=10)
            response.raise_for_status()

            branches = response.json()

            latest_major = -1
            latest_branch = None

            for branch in branches:
                name = branch["name"]

                match = re.match(r"releases/gcc-(\d+)$", name)

                if not match:
                    continue

                major = int(match.group(1))

                if major > latest_major:
                    latest_major = major
                    latest_branch = name

            if latest_branch is None:
                return False

            self.logger(f"Latest GCC version: {latest_major}")

            with open(self._lts_file, "w") as f:
                f.write(f"{latest_major}")

            self._current_version = latest_major
            self._docker_env_version = f"GCC_VERSION={self._current_version}"

        except Exception as ex:
            self.logger(ex)
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
            version=f"GCC_VERSION={self._stable_fallback_version}",
        )

        if result:
            self.append_compiled(service=service, version=self._stable_fallback_version)

        return result

    def build_x86_64(self):
        """
        GCC_VERSION=16 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up gcc-static-build-x86_64 --build
        """
        return self._build("gcc-static-build-x86_64")

    def build_x86(self):
        """
        GCC_VERSION=16 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up gcc-static-build-x86 --build
        """
        return self._build("gcc-static-build-x86")

    def build_arm64(self):
        """
        GCC_VERSION=16 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up gcc-static-build-arm64 --build
        """
        return self._build("gcc-static-build-arm64")

    def build_arm32(self):
        """
        GCC_VERSION=16 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up gcc-static-build-arm32 --build
        """
        return self._build("gcc-static-build-arm32")
