from src.abstract import Module
from src.docker_custom import CustomClient
import requests  # type: ignore[import-untyped]
from pathlib import Path
import os


class Postgre(Module):
    _url = "https://www.postgresql.org/versions.json"
    _target_name = "postgre"
    _lts_file = os.path.join(Path(__file__).resolve().parent, "lts_version")
    _stable_file = os.path.join(
        Path(__file__).resolve().parent, "stable_working_version"
    )
    _compiled_file = os.path.join(
        Path(__file__).resolve().parent, "compiled_versions"
    )
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
        self._docker_env_version = f"PG_VERSION={self._current_version}"

        self._stable_fallback_version = self.read_version_from_file(self._stable_file)

    def __str__(self):
        return self._target_name.upper()

    def update_version(self):
        try:

            versions = requests.get(self._url).json()
            latest = versions[-1]

            version = f"{latest['major']}.{latest['latestMinor']}"

            self.logger(f"Latest version: {version}")

            with open(self._lts_file, "w") as f:
                f.write(f"{version}")

            self._current_version = version
            self._docker_env_version = f"PG_VERSION={self._current_version}"

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
            version=f"PG_VERSION={self._stable_fallback_version}",
        )

        if result:
            self.append_compiled(
                service=service, version=self._stable_fallback_version
            )

        return result

    def build_x86_64(self):
        """
        PG_VERSION=18.3 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up pg-static-build-x86_64 --build
        """
        return self._build("pg-static-build-x86_64")

    def build_x86(self):
        """
        PG_VERSION=18.3 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up pg-static-build-x86 --build
        """
        return self._build("pg-static-build-x86")

    def build_arm64(self):
        """
        PG_VERSION=18.3 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up pg-static-build-arm64 --build
        """
        return self._build("pg-static-build-arm64")

    def build_arm32(self):
        """
        PG_VERSION=18.3 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up pg-static-build-arm32 --build
        """
        return self._build("pg-static-build-arm32")