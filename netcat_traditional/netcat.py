from src.abstract import Module
from src.docker_custom import CustomClient
from pathlib import Path
import os


class Netcat(Module):
    _url = ""
    _target_name = "netcat"
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
        self._docker_env_version = f"NETCAT_VERSION={self._current_version}"
        self._stable_fallback_version = self.read_version_from_file(self._stable_file)

    def __str__(self):
        return self._target_name.upper()

    def update_version(self):
        """
        GNU Netcat has been frozen at 0.7.1 since January 2004. The project
        has no release API and is effectively unmaintained — the official
        homepage (https://netcat.sourceforge.net) was last updated in 2013
        and the SVN repository is no longer accessible. Version is managed
        manually via the lts_version file.
        """
        self.logger("Netcat is frozen upstream — no version update performed")
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
            version=f"NETCAT_VERSION={self._stable_fallback_version}",
        )
        if result:
            self.append_compiled(service=service, version=self._stable_fallback_version)
        return result

    def build_x86_64(self):
        """
        NETCAT_VERSION=0.7.1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up netcat-static-build-x86_64 --build
        """
        return self._build("netcat-static-build-x86_64")

    def build_x86(self):
        """
        NETCAT_VERSION=0.7.1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up netcat-static-build-x86 --build
        """
        return self._build("netcat-static-build-x86")

    def build_arm64(self):
        """
        NETCAT_VERSION=0.7.1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up netcat-static-build-arm64 --build
        """
        return self._build("netcat-static-build-arm64")

    def build_arm32(self):
        """
        NETCAT_VERSION=0.7.1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up netcat-static-build-arm32 --build
        """
        return self._build("netcat-static-build-arm32")
