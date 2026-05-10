from src.abstract import Module
from src.docker_custom import CustomClient
import requests
from pathlib import Path
import os

class Postgre(Module):
    _url = "https://www.postgresql.org/versions.json"  # official JSON feed
    _target_name = "postgre"
    _lts_file = os.path.join(Path(__file__).resolve().parent, "lts_version")
    _compose_file = os.path.join(Path(__file__).resolve().parent, "docker-compose.yaml")
    _verbose = False
    _docker_client = None
    _current_version = "0" # updated at runtime

    def __init__(self, verbose, docker_client: CustomClient):
        self._verbose = verbose
        self._docker_client = docker_client
        self._current_version = self.read_version_from_file()
        pass

    def __str__(self):
        return self._target_name.upper()

    def _logger(self, string):
        if self._verbose:
            super().logger(f"{self}: {string}")

    def read_version_from_file(self) -> str:
        version = super().read_version_from_file(self._lts_file)
        self._logger(f"Version read from file {version}")
        return version

    def update_version(self):
        try :

            versions = requests.get(self._url).json()
            latest = versions[-1]  # sorted first-latest
            version  = f"{latest["major"]}.{latest['latestMinor']}"
            self._logger(f"Latest version: {version}")

            with open(self._lts_file,"w") as f:
                f.write(f"{version}")

            self._current_version = version

        except Exception as ex:
            print(ex)
            return False

        return True

    def build_x86_64(self):
        """
        HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up pg-static-build-x86_64
        """
        return self._docker_client.run(service="pg-static-build-x86_64", compose_file=self._compose_file)


    def build_x86(self):
        """
        HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up pg-static-build-x86
        """
        return self._docker_client.run(service="pg-static-build-x86", compose_file=self._compose_file)

    def build_arm64(self):
        """
        HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up pg-static-build-arm64
        """
        return self._docker_client.run(service="pg-static-build-arm64", compose_file=self._compose_file)

    def build_arm32(self):
        """
        HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up pg-static-build-arm32
        """
        return self._docker_client.run(service="pg-static-build-arm32", compose_file=self._compose_file)