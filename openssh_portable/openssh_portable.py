from src.abstract import Module
from src.docker_custom import CustomClient
from pathlib import Path
import requests as r
import re
import os


class Openssh_portable(Module):
    _url = "https://raw.githubusercontent.com/openssh/openssh-portable/master/version.h"
    _target_name = "openssh_portable"
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
        self._docker_env_version = f"OPENSSH_VERSION={self._current_version}"

        self._stable_fallback_version = self.read_version_from_file(self._stable_file)

    def __str__(self):
        return self._target_name.upper()

    def update_version(self):
        try:
            response = r.get(self._url, timeout=10)
            response.raise_for_status()

            content = response.text

            # Extract SSH_VERSION (e.g., "OpenSSH_10.3")
            ssh_version_match = re.search(
                r'#define\s+SSH_VERSION\s+"OpenSSH_(\d+\.\d+)"', content
            )
            # Extract SSH_PORTABLE (e.g., "p1")
            portable_match = re.search(r'#define\s+SSH_PORTABLE\s+"(p\d+)"', content)

            if not ssh_version_match or not portable_match:
                self.logger("Could not parse version.h")
                return False

            base_version = ssh_version_match.group(1)
            portable_suffix = portable_match.group(1)

            latest_version = f"{base_version}{portable_suffix}"
            self.logger(f"Latest OpenSSH version: {latest_version}")

            with open(self._lts_file, "w") as f:
                f.write(f"{latest_version}")

            self._current_version = latest_version
            self._docker_env_version = f"OPENSSH_VERSION={self._current_version}"

            return True

        except Exception as ex:
            self.logger(f"Error: {ex}")
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
            version=f"OPENSSH_VERSION={self._stable_fallback_version}",
        )

        if result:
            self.append_compiled(service=service, version=self._stable_fallback_version)

        return result

    def build_x86_64(self):
        """
        OPENSSH_VERSION=10.3p1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up openssh-portable-static-build-x86_64 --build
        """
        return self._build("openssh-portable-static-build-x86_64")

    def build_x86(self):
        """
        OPENSSH_VERSION=10.3p1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up openssh-portable-static-build-x86 --build
        """
        return self._build("openssh-portable-static-build-x86")

    def build_arm64(self):
        """
        OPENSSH_VERSION=10.3p1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up openssh-portable-static-build-arm64 --build
        """
        return self._build("openssh-portable-static-build-arm64")

    def build_arm32(self):
        """
        OPENSSH_VERSION=10.3p1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up openssh-portable-static-build-arm32 --build
        """
        return self._build("openssh-portable-static-build-arm32")
